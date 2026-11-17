import json
import urllib.parse
import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox

with open("diseases.json", "r", encoding="utf-8") as f:
    DISEASES_DB = json.load(f)

class HealthApp(App):
    def build(self):
        self.selected_symptoms = set()
        root = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        root.add_widget(Label(text="Full Body Health Checkup App", font_size='20sp', size_hint_y=None, height=40, bold=True))
        
        # Patient Inputs
        self.name_in = TextInput(hint_text="Name / Naam", multiline=False, size_hint_y=None, height=40)
        self.age_in = TextInput(hint_text="Age / Umar (Years)", input_filter='int', multiline=False, size_hint_y=None, height=40)
        self.weight_in = TextInput(hint_text="Weight / Wazan (kg)", input_filter='float', multiline=False, size_hint_y=None, height=40)
        self.height_in = TextInput(hint_text="Height / Lambai (cm)", input_filter='float', multiline=False, size_hint_y=None, height=40)
        self.city_in = TextInput(hint_text="City / Shehar (e.g., Ahmedabad)", multiline=False, size_hint_y=None, height=40)
        
        for widget in [self.name_in, self.age_in, self.weight_in, self.height_in, self.city_in]:
            root.add_widget(widget)
            
        root.add_widget(Label(text="Select Your Symptoms / Takleef Chunein:", size_hint_y=None, height=30, bold=True))
        
        # Scrollable Symptom Checkboxes
        scroll = ScrollView(size_hint=(1, 0.45))
        sym_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        sym_layout.bind(minimum_height=sym_layout.setter('height'))
        
        all_syms = {}
        for d in DISEASES_DB:
            for s in d["symptoms"]:
                all_syms[s["en"]] = f"{s['en']} / {s['hi']}"
                
        for en_key, label_text in sorted(all_syms.items()):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=35)
            cb = CheckBox(size_hint_x=0.15)
            cb.bind(active=lambda instance, value, k=en_key: self.toggle_sym(k, value))
            lbl = Label(text=label_text, halign='left', valign='middle', text_size=(250, None))
            row.add_widget(cb)
            row.add_widget(lbl)
            sym_layout.add_widget(row)
            
        scroll.add_widget(sym_layout)
        root.add_widget(scroll)
        
        # Diagnose Button
        btn = Button(text="Generate Diagnosis & Find Doctors", size_hint_y=None, height=50, background_color=(0.1, 0.6, 0.3, 1))
        btn.bind(on_press=self.diagnose)
        root.add_widget(btn)
        
        # Result Area
        res_scroll = ScrollView(size_hint=(1, 0.35))
        self.result_lbl = Label(text="Report yahan dikhegi...", size_hint_y=None, halign='left', valign='top', text_size=(320, None))
        self.result_lbl.bind(texture_size=self.result_lbl.setter('size'))
        res_scroll.add_widget(self.result_lbl)
        root.add_widget(res_scroll)
        
        return root

    def toggle_sym(self, sym, is_active):
        if is_active:
            self.selected_symptoms.add(sym)
        else:
            self.selected_symptoms.discard(sym)

    def diagnose(self, instance):
        try:
            w = float(self.weight_in.text or 0)
            h = float(self.height_in.text or 0)
            bmi = round(w / ((h / 100) ** 2), 2) if h > 0 else 0
        except ValueError:
            bmi = 0
            
        city = self.city_in.text.strip() or "India"
        matches = []
        for d in DISEASES_DB:
            d_syms = [s["en"] for s in d["symptoms"]]
            matched = len(self.selected_symptoms.intersection(set(d_syms)))
            if matched > 0:
                pct = round((matched / len(d_syms)) * 100, 1)
                matches.append((pct, d))
                
        matches.sort(reverse=True, key=lambda x: x[0])
        
        report = [f"Patient: {self.name_in.text} | Age: {self.age_in.text} | BMI: {bmi}\n"]
        if not matches:
            report.append("Koi matching disease nahi mili. Kripya doctor se milein.")
        else:
            for pct, d in matches:
                report.append(f"• {d['disease_en']} ({pct}% Match)")
                report.append(f"  Tests: {', '.join(d['pathology_tests'])}")
                report.append(f"  Care: {d['care_hi']}")
                report.append(f"  Best Specialist in {city}: {d['specialist']}\n")
            top_spec = matches[0][1]['specialist']
            maps_url = f"https://google.com{urllib.parse.quote(f'Best {top_spec} in {city}')}"
            webbrowser.open(maps_url)
            
        self.result_lbl.text = "\n".join(report)

if __name__ == "__main__":
    HealthApp().run()
