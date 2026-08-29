import sys
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))


from langchain_ollama import ChatOllama


from tools.file_tools import (
    list_files,
    read_file,
    write_file
)


from memory import add_change





llm = ChatOllama(
    model="qwen2.5-coder:7b",
    temperature=0
)






SYSTEM = """

You are a Senior Technical Documentation Engineer Agent.


Your responsibilities:


- Analyze any software project.
- Read source code.
- Understand architecture.
- Create professional documentation.



You create:


1. README.md

Include:

- Project introduction
- Features
- Installation
- Configuration
- Usage
- Examples



2. docs/API.md

Include:

- API endpoints
- Classes
- Methods
- Parameters
- Responses



3. docs/DEVELOPMENT.md

Include:

- Architecture
- Project structure
- Development workflow
- Contribution guide



4. docs/USER_GUIDE.md

Include:

- User instructions
- How to run the system
- Common operations



Rules:


- Work with any programming language.
- Do not modify source code.
- Only create documentation files.
- Return ONLY JSON.
- No markdown outside JSON.



Available action:



write_file:


{
"name":"write_file",
"arguments":{
"path":"README.md",
"content":"documentation"
}
}



"""









def clean_json(text):


    text=text.replace(
        "```json",
        ""
    )


    text=text.replace(
        "```",
        ""
    )


    return text.strip()










def execute(action):


    try:

        data=json.loads(
            clean_json(action)
        )


    except Exception as e:

        return f"JSON ERROR: {e}"





    if isinstance(data,list):


        results=[]


        for item in data:


            results.append(

                execute(
                    json.dumps(item)
                )

            )


        return "\n".join(results)







    name=data.get(
        "name"
    )


    args=data.get(
        "arguments",
        {}
    )





    if name=="read_file":


        return read_file.invoke(
            args
        )




    elif name=="write_file":


        return write_file.invoke(
            args
        )



    elif name=="list_files":


        return list_files.invoke(
            {}
        )



    return "Unknown action"









def documentation_agent(task):


    files=list_files.invoke({})



    project_content=""




    if files!="Project is empty":


        for file in files.splitlines():


            try:


                content=read_file.invoke(
                    {
                        "path":file
                    }
                )


                project_content += f"""

=====================

FILE:

{file}


CONTENT:

{content}


=====================

"""


            except:

                pass







    prompt=f"""

{SYSTEM}



Project Files:

{files}



Project Source:

{project_content}



Documentation Task:


{task}



Create complete professional documentation.



You must create these files:


1)

README.md



2)

docs/API.md



3)

docs/DEVELOPMENT.md



4)

docs/USER_GUIDE.md




Return ONLY JSON ARRAY.



Format:


[
{{
"name":"write_file",
"arguments":{{
"path":"README.md",
"content":"documentation"
}}
}}
]



"""





    response=llm.invoke(
        prompt
    )



    print("\nDOCUMENTATION MODEL:")

    print(response.content)





    result=execute(
        response.content
    )





    try:


        add_change(

            {

                "type":
                "documentation",

                "task":
                task,

                "result":
                result

            }

        )


    except:

        pass




    return result










if __name__=="__main__":


    while True:


        task=input(
            "\nDocumentation Task: "
        )


        if task.lower()=="exit":

            break




        result=documentation_agent(
            task
        )



        print(
            "\nRESULT:"
        )


        print(result)