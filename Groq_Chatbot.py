import os
import tkinter as tk
from tkinter import ttk, messagebox
from groq import Groq
import datetime

class ClaudeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chatbot")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a1a")

        # Custom theme
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

        # Configure ttk
        style = ttk.Style()
        style.theme_use('clam')  # Use 'clam' theme for better customization
        style.configure('TFrame', background=self.theme['background'])
        style.configure('TLabel', background=self.theme['background'], foreground=self.theme['text'])
        style.configure('TButton', background=self.theme['secondary'], foreground=self.theme['text'],
                         relief='flat', borderwidth=0, focuscolor=self.theme['hover'])
        style.map('TButton', background=[('active', self.theme['hover']), ('pressed', self.theme['primary'])])
        style.configure('TCombobox', background=self.theme['background'], foreground=self.theme['text'],
                        fieldbackground=self.theme['background'], bordercolor=self.theme['border'])
        style.configure('TScale', background=self.theme['background'], foreground=self.theme['text'],
                        troughcolor=self.theme['background'], bordercolor=self.theme['border'])

        # Create main container
        self.main_frame = ttk.Frame(self.root, style='TFrame')
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Prompt Input Section
        self.prompt_section = ttk.Frame(self.main_frame, style='TFrame')
        self.prompt_section.pack(fill="x", pady=10)

        self.prompt_label = ttk.Label(self.prompt_section, text="Enter your prompt:", style='TLabel')
        self.prompt_label.pack(anchor="w", padx=5, pady=5)

        # Text input for prompt
        self.prompt_entry = tk.Text(self.prompt_section,
                                  height=5,
                                  width=60,
                                  bg=self.theme['background'],
                                  fg=self.theme['text'],
                                  insertbackground=self.theme['text'],
                                  highlightthickness=2,
                                  highlightbackground=self.theme['border'],
                                  highlightcolor=self.theme['border'],
                                  borderwidth=2,
                                  relief='ridge')
        self.prompt_entry.pack(anchor="w", padx=5, pady=5)

        # Model Selection Section
        self.model_section = ttk.Frame(self.main_frame, style='TFrame')
        self.model_section.pack(fill="x", pady=10)

        self.model_label = ttk.Label(self.model_section, text="Select Model:", style='TLabel')
        self.model_label.pack(anchor="w", padx=5, pady=5)

        self.model = tk.StringVar()
        self.model.set("deepseek-r1-distill-llama-70b")  # default value
        self.model_option = ttk.Combobox(self.model_section,
                                       textvariable=self.model,
                                       values=['deepseek-r1-distill-llama-70b', 'llama-3.3-70b-versatile'])
        self.model_option.pack(anchor="w", padx=5, pady=5)

        # Temperature Adjustment Section
        self.temperature_section = ttk.Frame(self.main_frame, style='TFrame')
        self.temperature_section.pack(fill="x", pady=10)

        self.temperature_label = ttk.Label(self.temperature_section, text="Temperature:", style='TLabel')
        self.temperature_label.pack(anchor="w", padx=5, pady=5)

        self.temperature = tk.DoubleVar()
        self.temperature.set(0.4)  # default value
        self.temperature_scale = tk.Scale(self.temperature_section,
                                         from_=0.0,
                                         to=1.0,
                                         resolution=0.1,
                                         variable=self.temperature,
                                         orient="horizontal",
                                         bg=self.theme['background'],
                                         fg=self.theme['text'],
                                         highlightbackground=self.theme['background'],
                                         highlightcolor=self.theme['background'],
                                         troughcolor=self.theme['border'],
                                         borderwidth=0,
                                         relief='flat')
        self.temperature_scale.pack(anchor="w", padx=5, pady=5)

        # Button Section
        self.button_section = ttk.Frame(self.main_frame, style='TFrame')
        self.button_section.pack(fill="x", pady=10)

        self.generate_button = ttk.Button(self.button_section,
                                         text="Generate Response",
                                         command=self.generate_response,
                                         style='TButton')
        self.generate_button.pack(anchor="w", padx=5, pady=5)

        # Response Output Section
        self.response_section = ttk.Frame(self.main_frame, style='TFrame')
        self.response_section.pack(fill="both", expand=True, pady=10)

        self.response_label = ttk.Label(self.response_section, text="Response:", style='TLabel')
        self.response_label.pack(anchor="w", padx=5, pady=5)

        # Text output for response
        self.response_text = tk.Text(self.response_section,
                                   height=15,
                                   width=60,
                                   bg=self.theme['background'],
                                   fg=self.theme['text'],
                                   insertbackground=self.theme['text'],
                                   highlightthickness=2,
                                   highlightbackground=self.theme['border'],
                                   highlightcolor=self.theme['border'],
                                   borderwidth=2,
                                   relief='ridge')
        self.response_text.pack(anchor="w", fill="both", expand=True, padx=5, pady=5)
        self.response_text.config(state="disabled")

    def generate_response(self):
        try:
            # Hardcoded API key
            api_key = "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"

            prompt = self.prompt_entry.get("1.0", "end-1c")
            if not prompt:
                messagebox.showerror("Error", "Please enter a prompt")
                return

            model = self.model.get()
            temperature = self.temperature.get()

            client = Groq(api_key=api_key)

            # System message to guide the AI's response
            system_message = '''Answer in <thinking> and <reflection>
            You are an AI assistant designed to provide detailed, multi-perspective responses. Follow this structure:
            1. Begin with <thinking> (invisible to user):
               a. Analyze the question from 3 - 19 different angles
               b. Use the least amount of chains to cover all possible approaches
               c. For each approach:
                  i. Create <chain1>, <chain2>, <chain3>, <chain4>, <chain5>, <chain6>, <chain7>, <chain8>, <chain9>, <chain10>, <chain11>, <chain12>, <chain13>, <chain14>, <chain15>, <chain16>, <chain17>, <chain18>, <chain19> sections
                  ii. Develop full reasoning path for each chain
                  iii. Include mathematical/logical steps where applicable
                  iv. Consider opposing viewpoints in different chains
               d. Compare chains side-by-side
               e. Identify strengths/weaknesses of each approach

            2. Include <reflection> section (invisible to user):
               a. For each chain:
                  i. <validate> using domain-specific criteria
                  ii. <cross-check> with external knowledge
                  iii. <stress-test> edge cases
                  iv. <compare> chain outcomes
               b. Perform error analysis across all chains
               c. Resolve conflicts between chains
               d. Synthesize final conclusion from best elements

            3. Final output in <output>:
               a. Present unified answer combining best chain insights
               b. Acknowledge alternative approaches if relevant
               c. Provide confidence level assessment (1-100%)

            Rules:
            - Maintain 3 distinct chains minimum
            - Chains must represent fundamentally different approaches
            - No chain duplication - each must have unique reasoning
            - Tags must be on separate lines
            - Use markdown formatting for complex elements
            - If chains conflict, perform deeper analysis in reflection
            - Final output must synthesize multiple chain insights
            '''

            # API call
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": system_message},
                          {"role": "user", "content": prompt}],
                model=model,
                temperature=temperature
            )

            response = chat_completion.choices[0].message.content

            # Check for code blocks in the response
            if "```" in response:
                self.save_code_blocks(response)
            else:
                # Display response if no code blocks found
                self.response_text.config(state="normal")
                self.response_text.delete("1.0", "end")
                self.response_text.insert("1.0", response)
                self.response_text.config(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_code_blocks(self, response):
        """Extract and save code blocks from the response."""
        lines = response.split('\n')
        code_content = []
        in_code_block = False
        current_language = None
        code_blocks = []

        for line in lines:
            stripped_line = line.strip()

            # Detecting the start and end of code blocks
            if stripped_line.startswith('```'):
                if in_code_block:
                    # Save previous code block
                    code_blocks.append({'lang': current_language, 'content': code_content})
                    code_content = []
                in_code_block = not in_code_block

                # Set the language of the code block
                if in_code_block:
                    current_language = stripped_line.replace('```', '').strip() or 'txt'
            elif in_code_block:
                # Add code inside the block
                code_content.append(line)

        # Save the last code block if valid
        if code_content:
            code_blocks.append({'lang': current_language, 'content': code_content})

        if not code_blocks:
            messagebox.showinfo("No Code", "No valid code blocks found in the response.")
            return

        # Generate filename with timestamp and save each code block
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"generated_code_{timestamp}"

        for i, code_block in enumerate(code_blocks):
            lang = code_block['lang']
            content = code_block['content']

            # Get the file extension based on language
            ext = self.get_file_extension(lang)

            filename = f"{base_filename}_{i+1}.{ext}"
            counter = 1
            while os.path.exists(filename):
                filename = f"{base_filename}_{i+1}_{counter}.{ext}"
                counter += 1

            # Save to file
            with open(filename, 'w') as f:
                f.write('\n'.join(content))

            messagebox.showinfo("File Saved", f"Code saved as {filename}")

    def get_file_extension(self, language):
        """Map language to appropriate file extension."""
        ext_map = {
            'python': 'py',
            'java': 'java',
            'javascript': 'js',
            'csharp': 'cs',
            'cpp': 'cpp',
            'c': 'c',
            'ruby': 'rb',
            'swift': 'swift',
            'php': 'php',
            'go': 'go',
            'kotlin': 'kt',
            'rust': 'rs',
            'typescript': 'ts',
            'html': 'html',
            'css': 'css',
            'sql': 'sql',
            'bash': 'sh',
            'txt': 'txt'
        }
        return ext_map.get(language.lower(), 'txt')

if __name__ == "__main__":
    root = tk.Tk()
    app = ClaudeGUI(root)
    root.mainloop()
