# Git Lab Python Script Docker

This repository contains a Python script that runs within a Docker container. This README provides instructions on how to set up and run the script using Docker.

## Prerequisites

Make sure you have the following installed:

- Docker: [Installation Guide](https://docs.docker.com/get-docker/)
- Git (optional, for cloning this repository): [Installation Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

## Getting Started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ahmad899/solution.git
   cd solution
   ```

2. **Build the Docker Image:**

   ```bash
   docker build . -t gitlab-api --build-arg GITLAB_API_TOKEN=glpat-XXXXXX --build-arg GITLAB_API_URL=https://gitlab.com/api/v4
   ```

3. ## Run the Docker Image:

   **Help**

   ```bash
   docker run --rm gitlab-api -h
   ```

   **Get all merge requests or issues for a specific year.**

   ```bash
   docker run --rm gitlab-api get_mr_issues --option mr --year 2024
   ```

   **Grant or change user permissions on a group or project**

   ```bash
   docker run --rm gitlab-api grant_permission --username username --project-group (project or group) --role (Guest or Reporter or Developer or Maintainer or Owner)
   ```
