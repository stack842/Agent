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



llm = ChatOllama(
    model="qwen2.5-coder:7b",
    temperature=0
)





SYSTEM = """

You are a Senior Software Code Review Agent.

Your job:

- Review any software project.
- Analyze source code.
- Find bugs.
- Find security problems.
- Find architecture issues.
- Find performance problems.
- Suggest improvements.

You DO NOT modify source code.

You ONLY create review reports.



Rules:

- Return ONLY JSON.
- No markdown.
- No explanations.



Available actions:


read_file:

{
"name":"read_file",
"arguments":{
"path":"file/path"
}
}



write_file:

{
"name":"write_file",
"arguments":{
"path":"docs/review.md",
"content":"review report"
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



    # پشتیبانی از چند action

    if isinstance(data,list):

        results=[]

        for item in data:

            results.append(
                execute(
                    json.dumps(item)
                )
            )

        return "\n".join(results)




    name=data.get("name")

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









def reviewer_agent(task):


    files=list_files.invoke({})



    print("\nFILES REVIEW:")

    print(files)




    # خواندن همه فایل های پروژه

    project_content=""


    if files != "Project is empty":


        for file in files.splitlines():

            try:

                content=read_file.invoke(
                    {
                        "path":file
                    }
                )


                project_content += f"""

========================

FILE:

{file}


CONTENT:

{content}


========================


"""


            except Exception:

                pass





    prompt=f"""

{SYSTEM}



Project Files:

{files}



Project Content:

{project_content}



Review Task:

{task}



Analyze this project completely.


Create a professional review report.


The report must contain:


# Code Review Report


## Project Summary


## Files Reviewed


## Code Quality


## Bugs


## Security Issues


## Performance Issues


## Architecture Issues


## Recommendations



Return ONLY this JSON:


{{
"name":"write_file",
"arguments":{{
"path":"docs/review.md",
"content":"complete review"
}}
}}


"""



    response=llm.invoke(
        prompt
    )


    print("\nMODEL:")

    print(response.content)



    result=execute(
        response.content
    )


    return result











if __name__=="__main__":


    while True:


        task=input(
            "\nReviewer Task: "
        )


        if task.lower()=="exit":

            break



        result=reviewer_agent(
            task
        )


        print("\nRESULT:")

        print(result)