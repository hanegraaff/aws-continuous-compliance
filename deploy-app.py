"""Author: Mark Hanegraaff -- 2020
    Continuous Compliance App deploment script.
"""
import argparse
from zipfile import ZipFile
import logging
import os
import shutil
import boto3

log = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')


def deploy_app(deployment_zip: str, app_stack_name: str):
    def find_deployment_targets(app_stack_name: str):
        """
            Identifies all Lambda functions names that are exposed in the CloudFormation
            output. Looks for output names ending with "LambdaFunctionName"
        """

        cloudformation = boto3.resource('cloudformation')
        stack = cloudformation.Stack(app_stack_name)

        lambda_function_names = []

        outputs = stack.outputs

        for output in outputs:
            if output['OutputKey'].lower().endswith("lambdafunctionname"):
                lambda_function_names.append(output['OutputValue'])

        return lambda_function_names

    lambda_client = boto3.client('lambda')

    lambda_function_names = find_deployment_targets(app_stack_name)

    with open(deployment_zip, "rb") as deployment_zip_file:
        deployment_zip_contents = deployment_zip_file.read()

    if len(lambda_function_names) == 0:
        raise Exception(
            "No target lambda functions were found in the CloudFormation outputs")

    for name in lambda_function_names:
        log.info("Deploying %s to %s" % (deployment_zip, name) )
        lambda_client.update_function_code(
            FunctionName=name,
            ZipFile=deployment_zip_contents,
            Publish=True,
        )

def assemble_deployment_zip(src_dir_name: str, zipfile_name: str):
    """
        Creates the deployment zip file by including all python source files
    """
    def collect_artifact_names(src_dir_name: str):
        file_paths = []

        for root, directories, files in os.walk(src_dir_name):
            for filename in files:
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
        return file_paths

    allowed_file_extentions = ['.py']
    artifact_list = collect_artifact_names(src_dir_name)

    with ZipFile(zipfile_name, 'w') as zip:
        # writing each file one by one
        for artifact in artifact_list:
            ext = os.path.splitext(artifact)[1]

            if ext in allowed_file_extentions:
                log.info("Adding %s to %s" % (artifact, zipfile_name))
                archive_name = artifact.replace(src_dir_name, "")
                zip.write(artifact, archive_name)
            else:
                log.info("Skipping %s" % artifact)


def main():
    """
        Main Function for this script
    """

    deploy_dir = "./deploy"
    deploy_archive = "%s/cc-app.zip" % deploy_dir

    description = """
                Deploys the continuous compliance app to the desgnated Lambda Functions
            """

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-cf_stack_name", help="Continuous Compliance App CloudFormation stack name",
                        type=str, required=True)

    args = parser.parse_args()

    try:

        log.info("Deployment artifact name: %s" % deploy_archive)
        log.info("Cleaning Deployment Directory")
        shutil.rmtree(deploy_dir)

        log.info("Creating Deployment Directory")
        os.mkdir(deploy_dir, 0o777)

        log.info(args.cf_stack_name)

        log.info("Generating Deployment Artifact")
        assemble_deployment_zip('./src', deploy_archive)

        log.info("Deploying App")
        deploy_app(deploy_archive, args.cf_stack_name)

        log.info("Done!")
    except Exception as e:
        log.error("There was an error deplying application, beause: %s" % str(e))


if __name__ == "__main__":
    main()
