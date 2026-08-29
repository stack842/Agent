import sys
from pathlib import Path
import json
import subprocess
import importlib.util
import traceback


ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))


from tools.file_tools import (
    write_file,
    list_files
)


from memory import (
    load_state,
    save_state,
    add_test,
    add_issue
)



PROJECT_PATH = ROOT / "project"



# =========================
# Find Files
# =========================

def find_python_files():

    files=[]

    if PROJECT_PATH.exists():

        for file in PROJECT_PATH.rglob("*.py"):

            if "__pycache__" not in str(file):

                files.append(file)


    return files





# =========================
# Run Python
# =========================

def run_file(file):

    try:

        result=subprocess.run(

            [
                "python",
                str(file)
            ],

            capture_output=True,

            text=True,

            timeout=60

        )


        return {

            "file":str(file),

            "status":
                "PASS"
                if result.returncode==0
                else "FAIL",

            "stdout":result.stdout,

            "stderr":result.stderr,

            "return_code":result.returncode

        }


    except Exception as e:


        return {

            "file":str(file),

            "status":"ERROR",

            "error":str(e)

        }






# =========================
# Import Test
# =========================

def test_import(file):

    try:

        spec=importlib.util.spec_from_file_location(

            file.stem,

            file

        )


        module=importlib.util.module_from_spec(
            spec
        )


        spec.loader.exec_module(
            module
        )


        return {

            "file":str(file),

            "status":"IMPORT_PASS"

        }


    except Exception:


        return {

            "file":str(file),

            "status":"IMPORT_FAIL",

            "error":traceback.format_exc()

        }






# =========================
# Class Test
# =========================

def test_classes(file):

    results=[]


    try:


        spec=importlib.util.spec_from_file_location(

            file.stem,

            file

        )


        module=importlib.util.module_from_spec(
            spec
        )


        spec.loader.exec_module(
            module
        )



        for name in dir(module):


            obj=getattr(
                module,
                name
            )



            if isinstance(obj,type):


                try:

                    instance=obj()


                except Exception as e:


                    results.append({

                        "class":name,

                        "status":"INIT_FAILED",

                        "error":str(e)

                    })

                    continue





                methods=[

                    x for x in dir(instance)

                    if not x.startswith("_")

                    and callable(
                        getattr(instance,x)
                    )

                ]



                for method in methods:


                    try:


                        output=getattr(
                            instance,
                            method
                        )()



                        results.append({

                            "class":name,

                            "method":method,

                            "status":"PASS",

                            "output":str(output)

                        })



                    except Exception as e:


                        results.append({

                            "class":name,

                            "method":method,

                            "status":"FAIL",

                            "error":str(e)

                        })



    except Exception:


        results.append({

            "file":str(file),

            "status":"ERROR",

            "error":traceback.format_exc()

        })



    return results






# =========================
# Run pytest
# =========================

def run_pytest():


    tests_path=PROJECT_PATH / "tests"


    if not tests_path.exists():

        return {

            "status":"SKIPPED",

            "message":"No tests folder"

        }




    try:


        result=subprocess.run(

            [
                "pytest",
                str(tests_path)
            ],

            capture_output=True,

            text=True,

            timeout=120

        )



        return {

            "status":

                "PASS"
                if result.returncode==0
                else "FAIL",

            "stdout":result.stdout,

            "stderr":result.stderr

        }



    except Exception as e:


        return {

            "status":"ERROR",

            "error":str(e)

        }








# =========================
# Report
# =========================

def create_report(data):


    report="""

# Software Test Report


"""


    report+="## Python File Execution\n\n"


    for item in data["execution"]:


        report+=f"""

File:
{item.get('file')}


Status:
{item.get('status')}


Error:
{item.get('stderr','')}

------------------

"""



    report+="\n## Import Tests\n\n"



    for item in data["imports"]:


        report+=f"""

File:
{item.get('file')}


Status:
{item.get('status')}


------------------

"""



    report+="\n## Class Tests\n\n"



    for item in data["classes"]:


        report+=f"""

Class:
{item.get('class')}


Method:
{item.get('method')}


Status:
{item.get('status')}


Output:
{item.get('output',item.get('error',''))}


------------------

"""



    report+="\n## Pytest\n\n"


    report+=str(
        data["pytest"]
    )


    return report







# =========================
# Tester Agent
# =========================

def tester_agent(task):


    print("\nScanning project...")


    files=find_python_files()



    if not files:


        return "No python files found"




    execution=[]

    imports=[]

    classes=[]




    for file in files:


        print(
            "Testing:",
            file
        )


        execution.append(

            run_file(file)

        )


        imports.append(

            test_import(file)

        )


        classes.extend(

            test_classes(file)

        )




    pytest_result=run_pytest()



    results={


        "execution":

        execution,


        "imports":

        imports,


        "classes":

        classes,


        "pytest":

        pytest_result

    }




    report=create_report(
        results
    )




    result=write_file.invoke({

        "path":

        "docs/test_report.md",


        "content":

        report

    })




    # Memory update


    add_test(
        results
    )



    for item in execution:


        if item["status"]!="PASS":

            add_issue(
                item
            )



    return result








if __name__=="__main__":


    while True:


        task=input(

            "\nTester Task: "

        )



        if task.lower()=="exit":

            break



        result=tester_agent(
            task
        )


        print(
            "\nRESULT:"
        )


        print(result)