import os
import tkinter as tk
from tkinter import ttk, messagebox
from groq import Groq
import re
from typing import Dict, Tuple

class TemperatureRegulator:
    """Handles automatic temperature regulation based on prompt analysis"""
    
    def __init__(self):
        self.temp_ranges = {
            'creative': (0.7, 0.9),
            'analytical': (0.1, 0.3),
            'balanced': (0.4, 0.6)
        }
        
        self.task_indicators = {
            'creative': [
                'imagine', 'create', 'story', 'design', 'generate',
                'brainstorm', 'innovative', 'creative', 'write', 'describe'
            ],
            'analytical': [
                'analyze', 'calculate', 'solve', 'explain', 'compare',
                'evaluate', 'examine', 'investigate', 'reason', 'logic'
            ]
        }

    def calculate_optimal_temperature(self, prompt: str) -> float:
        """Calculate optimal temperature based on prompt analysis"""
        task_type, confidence = self._analyze_task_type(prompt)
        temp_min, temp_max = self.temp_ranges[task_type]
        
        complexity = self._calculate_complexity(prompt)
        base_temp = temp_min + (temp_max - temp_min) * complexity
        
        if confidence < 0.8:
            balanced_temp = 0.5
            adjustment = (1 - confidence) * 0.5
            base_temp = base_temp * (1 - adjustment) + balanced_temp * adjustment
            
        return round(min(max(base_temp, 0.1), 0.9), 2)

    def _analyze_task_type(self, prompt: str) -> Tuple[str, float]:
        """Determine task type and confidence level"""
        prompt = prompt.lower()
        scores = {'creative': 0, 'analytical': 0, 'balanced': 1}
        
        for task_type, keywords in self.task_indicators.items():
            for keyword in keywords:
                if keyword in prompt:
                    scores[task_type] += 1
        
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
            
        task_type = max(scores.items(), key=lambda x: x[1])[0]
        return task_type, scores[task_type]

    def _calculate_complexity(self, prompt: str) -> float:
        """Calculate prompt complexity score"""
        words = len(prompt.split())
        sentences = prompt.split('.')
        
        word_factor = min(words / 100, 1.0)
        avg_sentence_length = words / max(len(sentences), 1)
        sentence_complexity = min(avg_sentence_length / 20, 1.0)
        question_factor = min(prompt.count('?') / 3, 1.0)
        special_chars = len(re.findall(r'[^a-zA-Z0-9\s]', prompt))
        special_char_factor = min(special_chars / len(prompt), 1.0)
        
        complexity = (
            word_factor * 0.3 +
            sentence_complexity * 0.3 +
            question_factor * 0.2 +
            special_char_factor * 0.2
        )
        
        return min(max(complexity, 0.0), 1.0)

class AIChat:
    """Handles AI chat functionality and API interactions"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.system_message = '''Answer in <thinking> and <reflection>
You are an AI assistant designed to provide detailed, multi-perspective responses. Follow this structure:

1. Begin with <thinking> (invisible to user):
   - Analyze from multiple angles
   - Consider different approaches
   - Develop full reasoning paths
   - Include mathematical/logical steps where applicable

2. Include <reflection> section (invisible to user):
   - Validate using domain-specific criteria
   - Cross-check with external knowledge
   - Stress-test edge cases
   - Compare outcomes
   - Resolve conflicts
   - Synthesize conclusion

3. Final output in <output>:
   - Present unified answer
   - Acknowledge alternatives if relevant
   - Provide confidence level (1-100%)

Maintain at least 3 distinct reasoning chains and synthesize insights in final output.'''

    def generate_response(self, prompt: str, model: str, temperature: float) -> str:
        """Generate AI response using specified parameters"""
        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt},
                ],
                model=model,
                temperature=temperature
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"API Error: {str(e)}")

class ChatGUI:
    """Main GUI application for AI chat interface"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_theme()
        self.setup_styles()
        self.create_widgets()
        self.setup_bindings()
        
        # Initialize components
        self.temp_regulator = TemperatureRegulator()
        self.ai_chat = AIChat(api_key="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")  # Replace with your API key

    def setup_window(self):
        """Configure main window properties"""
        self.root.title("AI Chat Interface")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a1a")

    def create_theme(self):
        """Define application theme colors"""
        self.theme = {
            'background': '#1a1a1a',
            'text': '#ffffff',
            'primary': '#4a90e2',
            'secondary': '#e2a90a',
            'success': '#34c759',
            'error': '#e23a3a',
            'hover': '#2a2a2a',
            'border': '#3a3a3a'
        }

    def setup_styles(self):
        """Configure ttk styles for widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background=self.theme['background'])
        style.configure('TLabel', background=self.theme['background'], 
                       foreground=self.theme['text'])
        style.configure('TButton', background=self.theme['secondary'],
                       foreground=self.theme['text'], relief='flat', 
                       borderwidth=0)
        style.configure('TCheckbutton', background=self.theme['background'],
                       foreground=self.theme['text'])
        style.map('TButton', 
                 background=[('active', self.theme['hover']),
                            ('pressed', self.theme['primary'])])

    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Prompt section
        self.create_prompt_section()
        
        # Model selection section
        self.create_model_section()
        
        # Temperature section
        self.create_temperature_section()
        
        # Response section
        self.create_response_section()

    def create_prompt_section(self):
        """Create prompt input area"""
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill="x", pady=10)
        
        ttk.Label(frame, text="Enter your prompt:").pack(anchor="w", padx=5, pady=5)
        
        self.prompt_entry = tk.Text(frame, height=5, width=60,
                                  bg=self.theme['background'],
                                  fg=self.theme['text'],
                                  insertbackground=self.theme['text'],
                                  relief='solid', borderwidth=1)
        self.prompt_entry.pack(fill="x", padx=5, pady=5)

    def create_model_section(self):
        """Create model selection area"""
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill="x", pady=10)
        
        ttk.Label(frame, text="Select Model:").pack(anchor="w", padx=5, pady=5)
        
        self.model = tk.StringVar(value="deepseek-r1-distill-llama-70b")
        self.model_combo = ttk.Combobox(frame, textvariable=self.model,
                                      values=['deepseek-r1-distill-llama-70b',
                                             'llama-3.3-70b-versatile'])
        self.model_combo.pack(anchor="w", padx=5, pady=5)

    def create_temperature_section(self):
        """Create temperature control area"""
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill="x", pady=10)
        
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill="x")
        
        ttk.Label(control_frame, text="Temperature:").pack(side="left", padx=5)
        
        self.auto_temp = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Auto-regulate",
                       variable=self.auto_temp,
                       command=self.toggle_temperature).pack(side="left", padx=5)
        
        self.temperature = tk.DoubleVar(value=0.4)
        self.temp_scale = tk.Scale(frame, from_=0.0, to=1.0, resolution=0.1,
                                 variable=self.temperature, orient="horizontal",
                                 bg=self.theme['background'],
                                 fg=self.theme['text'],
                                 troughcolor=self.theme['border'],
                                 state='disabled')
        self.temp_scale.pack(fill="x", padx=5, pady=5)

        # Generate button
        ttk.Button(frame, text="Generate Response",
                  command=self.generate_response).pack(anchor="w", padx=5, pady=10)

    def create_response_section(self):
        """Create response output area"""
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill="both", expand=True, pady=10)
        
        ttk.Label(frame, text="Response:").pack(anchor="w", padx=5, pady=5)
        
        self.response_text = tk.Text(frame, height=15, width=60,
                                   bg=self.theme['background'],
                                   fg=self.theme['text'],
                                   insertbackground=self.theme['text'],
                                   relief='solid', borderwidth=1)
        self.response_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.response_text.config(state="disabled")

    def setup_bindings(self):
        """Setup keyboard bindings"""
        self.prompt_entry.bind('<Return>', self.on_enter)
        self.prompt_entry.bind('<Shift-Return>', self.on_shift_enter)
        self.prompt_entry.bind('<KeyRelease>', self.on_prompt_change)

    def toggle_temperature(self):
        """Toggle between manual and automatic temperature control"""
        if self.auto_temp.get():
            self.temp_scale.config(state="disabled")
            self.update_temperature()
        else:
            self.temp_scale.config(state="normal")

    def update_temperature(self):
        """Update temperature based on current prompt"""
        if self.auto_temp.get():
            prompt = self.prompt_entry.get("1.0", "end-1c")
            if prompt.strip():
                temp = self.temp_regulator.calculate_optimal_temperature(prompt)
                self.temperature.set(temp)

    def on_prompt_change(self, event=None):
        """Handle prompt changes"""
        self.update_temperature()

    def on_enter(self, event):
        """Handle Enter key press"""
        self.generate_response()
        return 'break'

    def on_shift_enter(self, event):
        """Handle Shift+Enter key press"""
        self.prompt_entry.insert('insert', '\n')
        return 'break'

    def generate_response(self):
        """Generate AI response"""
        try:
            prompt = self.prompt_entry.get("1.0", "end-1c").strip()
            if not prompt:
                messagebox.showerror("Error", "Please enter a prompt")
                return

            self.update_temperature()
            
            response = self.ai_chat.generate_response(
                prompt=prompt,
                model=self.model.get(),
                temperature=self.temperature.get()
            )
            
            self.response_text.config(state="normal")
            self.response_text.delete("1.0", "end")
            self.response_text.insert("1.0", response)
            self.response_text.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGUI(root)
    root.mainloop()
