import os
from dotenv import load_dotenv
import json
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)

def generate_component_data(prompt):
    llm = genai.GenerativeModel("gemini-1.5-flash")

    prompt_template = PromptTemplate(
        input_variables=["prompt"],
        template="""
        You are a code generator AI. Given the following description, generate a JSON response with a list of components. 
        Each component should have "name", "html", and "css" keys. Here is an example:
        {{
          "components": [
            {{
              "name": "Navbar",
              "html": "<nav><ul><li>Home</li><li>About</li><li>Contact</li></ul></nav>",
              "css": "nav {{ background-color: #333; padding: 10px; }} nav ul {{ list-style: none; padding: 0; }} nav ul li {{ display: inline; color: white; margin-right: 15px; }}"
            }},
            {{
              "name": "MainContainer",
              "html": "<main><h1>Welcome</h1><p>This is the main content area.</p></main>",
              "css": "main {{ padding: 20px; background-color: #f4f4f4; }} main h1 {{ color: #333; }} main p {{ color: #666; }}"
            }},
            {{
              "name": "SettingDropdown",
              "html": "<div class='dropdown'><button>Settings</button><div class='dropdown-content'><a href='#'>Profile</a><a href='#'>Settings</a><a href='#'>Logout</a></div></div>",
              "css": ".dropdown {{ position: relative; display: inline-block; }} .dropdown-content {{ display: none; position: absolute; background-color: #f9f9f9; box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2); }} .dropdown:hover .dropdown-content {{ display: block; }}"
            }}
          ]
        }}
        Description: {prompt}
        """
    )

    formatted_prompt = prompt_template.format(prompt=prompt)
    response = llm.generate_content(formatted_prompt)
    
    
    nested_result = response._result

    json_string = nested_result.candidates[0].content.parts[0].text

    json_string = json_string.strip("```json").strip("```").strip()

    component_data = json.loads(json_string)

    return component_data

def save_component_data_to_file(component_data, filename):
    with open(filename, 'w') as file:
        json.dump(component_data, file, indent=4)  


def create_react_files(components):
    src_dir = "../frontend/generated/src"
    os.makedirs(f"{src_dir}/components", exist_ok=True)

    for component in components:
        component_name = component["name"]
        component_dir = f"{src_dir}/components/{component_name}"
        os.makedirs(component_dir, exist_ok=True)

        with open(f"{component_dir}/{component_name}.jsx", "w") as jsx_file:
            jsx_content = f"""
import './{component_name}.css';

const {component_name} = () => (
    <>
    {component["html"]}
    </>
);

export default {component_name};
"""
            jsx_file.write(jsx_content)

        with open(f"{component_dir}/{component_name}.css", "w") as css_file:
            css_file.write(component["css"])

def update_main_files(components):
    src_dir = "../frontend/generated/src"

    # Update App.js to import and render components
    with open(f"{src_dir}/App.js", "w") as app_file:
        imports = "\n".join(
            [f"import {comp['name']} from './components/{comp['name']}/{comp['name']}';" for comp in components]
        )
        renders = "\n".join([f"<{comp['name']} />" for comp in components])

        app_content = f"""
import React from 'react';
{imports}

function App() {{
    return (
        <div>
            {renders}
        </div>
    );
}}

export default App;
"""
        app_file.write(app_content)

    # Ensure index.js renders App
    with open(f"{src_dir}/index.js", "w") as index_file:
        index_content = """
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css';

ReactDOM.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
    document.getElementById('root')
);
"""
        index_file.write(index_content)


def main():
    prompt = "Create a basic React app with components for a Navbar, MainContainer, and SettingDropdown."
    component_data = generate_component_data(prompt)
    create_react_files(component_data["components"])
    update_main_files(component_data["components"])
    print("React app files generated successfully.")

if __name__ == "__main__":
    main()
