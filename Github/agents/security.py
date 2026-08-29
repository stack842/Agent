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


from memory import add_issue





llm = ChatOllama(
    model="qwen2.5-coder:7b",
    temperature=0
)






SYSTEM = """

You are a Senior Cyber Security Engineer Agent.


Your responsibilities:


- Review any software project.
- Find security vulnerabilities.
- Analyze source code.
- Check authentication problems.
- Check authorization problems.
- Check unsafe input handling.
- Check secrets exposure.
- Check dependency risks.
- Suggest security improvements.



You DO NOT modify source code.


You create security reports.



Rules:

Return ONLY JSON.

No markdown outside JSON.



Available actions:


read_file:


{
"name":"read_file",
"arguments":{
"path":"file.py"
}
}




write_file:


{
"name":"write_file",
"arguments":{
"path":"docs/security_report.md",
"content":"security report"
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











def security_agent(task):


    files=list_files.invoke({})



    project_content=""




    if files and files!="Project is empty":


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



Project Content:

{project_content}



Security Task:

{task}



Create a complete security report.



Report structure:


# Security Report


## Security Summary


## Vulnerabilities Found


For each issue include:


- Severity
- Location
- Description
- Risk
- Recommendation



## Authentication Issues


## Authorization Issues


## Data Protection


## Dependency Risks


## Security Improvements



Return ONLY JSON:


{{
"name":"write_file",
"arguments":{{
"path":"docs/security_report.md",
"content":"security report"
}}
}}


"""




    response=llm.invoke(
        prompt
    )


    print("\nSECURITY MODEL:")

    print(response.content)





    result=execute(
        response.content
    )



    try:

        add_issue(
            {
                "type":"security_review",
                "result":result
            }
        )


    except:

        pass



    return result










if __name__=="__main__":


    while True:


        task=input(
            "\nSecurity Task: "
        )


        if task.lower()=="exit":

            break




        result=security_agent(
            task
        )


        print(
            "\nRESULT:"
        )


        print(result)