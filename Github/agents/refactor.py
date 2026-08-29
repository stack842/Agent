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

You are a Senior Software Refactoring Agent.


Your responsibilities:


- Analyze existing source code.
- Improve code quality.
- Remove duplicated code.
- Improve architecture.
- Improve readability.
- Improve maintainability.
- Improve performance.
- Apply clean code principles.



You ARE allowed to modify source code.


Rules:


- Keep existing functionality.
- Do not break APIs.
- Write production quality code.
- Return ONLY JSON.
- No markdown.



Available actions:



read_file:


{
"name":"read_file",
"arguments":{
"path":"src/file.py"
}
}




write_file:


{
"name":"write_file",
"arguments":{
"path":"src/file.py",
"content":"improved code"
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



    return "Unknown action"









def refactor_agent(task):


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



Source Code:

{project_content}



Refactor Task:


{task}



Analyze the code.


If improvement is needed:

Rewrite the complete file.


Return JSON ARRAY.


Example:


[
{{
"name":"write_file",
"arguments":{{
"path":"src/example.py",
"content":"new improved code"
}}
}}
]



Only return files that need modification.



"""




    response=llm.invoke(
        prompt
    )



    print("\nREFACTOR MODEL:")

    print(response.content)





    result=execute(
        response.content
    )





    try:


        add_change(

            {

                "type":
                "refactor",

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
            "\nRefactor Task: "
        )


        if task.lower()=="exit":

            break




        result=refactor_agent(
            task
        )



        print(
            "\nRESULT:"
        )


        print(result)