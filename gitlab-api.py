#!/usr/bin/env python3

import os
import sys
import requests
import json
import argparse
from dotenv import load_dotenv

load_dotenv()

GITLAB_API_TOKEN = os.getenv("GITLAB_API_TOKEN")
GITLAB_API_URL = os.getenv("GITLAB_API_URL")

# Check if env is set or not
if not GITLAB_API_URL or not GITLAB_API_TOKEN:
    raise EnvironmentError(
        "Please set the GITLAB_API_URL and GITLAB_API_TOKEN environment variables"
    )

headers = {"Authorization": f"Bearer {GITLAB_API_TOKEN}"}

role_dict = {
    "Guest": 10,
    "Reporter": 20,
    "Developer": 30,
    "Maintainer": 40,
    "Owner": 50,
}


def grant_permission(username, repo_group_name, role):
    user_id = get_user_id(username)
    project_or_group_var = project_or_group(repo_group_name)
    repo_group_id = get_project_or_group_id(repo_group_name, project_or_group_var)

    if role not in role_dict:
        print(f"Invalid role: {role}. Valid roles are: {list(role_dict.keys())}")
        return

    # Check if user is already a member in the group/project
    if is_member(user_id, repo_group_id, project_or_group_var):
        change_role(user_id, repo_group_id, role, project_or_group_var)
    else:
        grant_role(user_id, repo_group_id, role, project_or_group_var)


def get_mr_issues(mr_issues, year):
    try:
        if mr_issues not in ["mr", "issues"]:
            raise ValueError("the name must be either 'mr', 'issues' ")

        if not (1000 <= year <= 9999):
            raise ValueError("year must be a 4-digit integer")

        if mr_issues == "mr":
            request_type = "merge_requests"
        else:
            request_type = "issues"

        # Get user ID
        params = {
            "created_after": f"{year}-01-01T00:00:00Z",
            "created_before": f"{year}-12-31T23:59:59Z",
        }
        response = requests.get(
            f"{GITLAB_API_URL}/{request_type}", headers=headers, params=params
        )
        response.raise_for_status()

        if len(response.json()):
            print(json.dumps(response.json(), indent=2))

        else:
            print(f"There are no {mr_issues} this year: {year}")
            sys.exit(1)

    except requests.exceptions.HTTPError as http_err:
        print(f"MR ISSUES HTTP error occurred: {http_err.response.text}")
        sys.exit(1)


def get_user_id(username):
    try:
        response = requests.get(
            f"{GITLAB_API_URL}/users?username={username}", headers=headers
        )
        response.raise_for_status()
        users = response.json()
        if users:
            user_id = users[0].get("id")
            if user_id:
                return user_id
            else:
                print(f"No user ID found for username: {username}")
                sys.exit(1)
        else:
            print(f"No users found for username: {username}")
            sys.exit(1)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err.response.text}")
        sys.exit(1)


def get_admin_name():
    try:
        response = requests.get(f"{GITLAB_API_URL}/user", headers=headers)
        response.raise_for_status()
        return response.json()["username"]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err.response.text}")
        sys.exit(1)


def is_member(user_id, repo_group_id, project_or_group):
    try:
        response = requests.get(
            f"{GITLAB_API_URL}/{project_or_group}/{repo_group_id}/members/all/{user_id}",
            headers=headers,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 404:
            return False
        else:
            print(f"HTTP error occurred: {http_err.response.text}")
            sys.exit(1)


def project_or_group(repo_group_name):
    try:
        admin_name = get_admin_name()
        groups_response = requests.get(
            f"{GITLAB_API_URL}/groups?search={repo_group_name}", headers=headers
        )
        projects_response = requests.get(
            f"{GITLAB_API_URL}/users/{admin_name}/projects?search={repo_group_name}",
            headers=headers,
        )

        groups_response.raise_for_status()
        projects_response.raise_for_status()

        if groups_response.json():
            return "groups"
        elif projects_response.json():
            return "projects"
        else:
            print(f"No project or group was found: {repo_group_name}")
            sys.exit(1)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err.response.text}")
        sys.exit(1)


def get_project_or_group_id(repo_group_name, project_or_group):
    try:
        admin_name = get_admin_name()
        if project_or_group == "projects":
            response = requests.get(
                f"{GITLAB_API_URL}/{project_or_group}/{admin_name}%2F{repo_group_name}",
                headers=headers,
            )
        else:
            response = requests.get(
                f"{GITLAB_API_URL}/{project_or_group}/{repo_group_name}",
                headers=headers,
            )
        response.raise_for_status()
        return response.json()["id"]
    except requests.exceptions.HTTPError as http_err:
        print(f"Get project or group ID HTTP error occurred: {http_err.response.text}")
        sys.exit(1)


def change_role(user_id, repo_group_id, role, project_or_group):
    try:
        data = {"user_id": user_id, "access_level": role_dict[role]}
        response = requests.put(
            f"{GITLAB_API_URL}/{project_or_group}/{repo_group_id}/members/{user_id}",
            headers=headers,
            data=data,
        )
        response.raise_for_status()
        print("ROLE CHANGED")
    except requests.exceptions.HTTPError as http_err:
        print(f"Change role HTTP error occurred: {http_err.response.text}")
        sys.exit(1)


def grant_role(user_id, repo_group_id, role, project_or_group):
    try:
        data = {"user_id": user_id, "access_level": role_dict[role]}
        response = requests.post(
            f"{GITLAB_API_URL}/{project_or_group}/{repo_group_id}/members",
            headers=headers,
            data=data,
        )
        response.raise_for_status()
        print("USER GRANTED")
    except requests.exceptions.HTTPError as http_err:
        print(f"Grant role HTTP error occurred: {http_err.response.text}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="Gitlab API", description="Get gitlab api argument"
    )

    sub_parsers = parser.add_subparsers(dest="command")

    parser_grant_permission = sub_parsers.add_parser(
        "grant_permission",
        help="Grant or change user permissions on a group or project",
    )
    parser_grant_permission.add_argument(
        "--username",
        type=str,
        required=True,
        help="The username for which you want to grant or change permissions.",
    )
    parser_grant_permission.add_argument(
        "--project-group", type=str, required=True, help="The Gitlap project or group"
    )
    parser_grant_permission.add_argument(
        "--role",
        type=str,
        required=True,
        choices=["Guest", "Reporter", "Developer", "Maintainer", "Owner"],
        help="The role you want to grant or change for the user.",
    )
    parser_get_mr_issues = sub_parsers.add_parser(
        "get_mr_issues", help="Get all merge requests or issues for a specific year."
    )

    parser_get_mr_issues.add_argument(
        "--option",
        type=str,
        required=True,
        choices=["mr", "issues"],
        help="merge request 'mr' or 'issues'",
    )
    parser_get_mr_issues.add_argument(
        "--year",
        type=int,
        required=True,
        help="The year for which you want to retrieve all issues or merge requests.",
    )

    # This will print help if no arguments are given.
    args = parser.parse_args(args=None if sys.argv[1:] else ["--help"])

    if args.command == "grant_permission":
        grant_permission(args.username, args.project_group, args.role)
    elif args.command == "get_mr_issues":
        get_mr_issues(args.option, args.year)
    else:
        print("Not implemented")
        sys.exit(1)


if __name__ == "__main__":
    main()
