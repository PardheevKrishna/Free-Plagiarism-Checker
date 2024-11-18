
---

# Free Plagiarism Checker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![GitHub Issues](https://img.shields.io/github/issues/PardheevKrishna/Free-Plagiarism-Checker)](https://github.com/PardheevKrishna/Free-Plagiarism-Checker/issues)
[![GitHub Forks](https://img.shields.io/github/forks/PardheevKrishna/Free-Plagiarism-Checker)](https://github.com/PardheevKrishna/Free-Plagiarism-Checker/network)
[![GitHub Stars](https://img.shields.io/github/stars/PardheevKrishna/Free-Plagiarism-Checker)](https://github.com/PardheevKrishna/Free-Plagiarism-Checker/stargazers)

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Steps](#steps)
- [Configuration](#configuration)
  - [Set Up Environment Variables](#set-up-environment-variables)
  - [Obtaining API Keys](#obtaining-api-keys)
- [Usage](#usage)
  - [Running the Script](#running-the-script)
  - [Running in Visual Studio Code](#running-in-visual-studio-code)
- [Project Structure](#project-structure)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Description

The **Free Plagiarism Checker** is a Python-based application designed to detect potential instances of plagiarism by comparing text against web sources. Utilizing the power of the Google Custom Search API, it analyzes text for similarities, generates comprehensive HTML and CSV reports, and provides relevant snippets from the web to support the findings.

## Features

- **Environment Variable Management**: Securely load API keys and configuration from a `.env` file.
- **Text Analysis**: Analyze text for plagiarism with configurable similarity thresholds.
- **Report Generation**: Produce detailed HTML and CSV reports highlighting plagiarized content.
- **Scalability**: Efficiently handle large volumes of data and multiple data streams.
- **Modular Design**: Easily extendable for additional features and integrations.
- **User-Friendly Interface**: Clear and concise reports for easy interpretation of results.

## Installation

### Prerequisites

- **Python 3.8+**: Ensure you have Python installed. You can download it from [here](https://www.python.org/downloads/).
- **Git**: To clone the repository. Download it from [here](https://git-scm.com/downloads).

### Steps

1. **Clone the Repository**

    ```sh
    git clone https://github.com/PardheevKrishna/Free-Plagiarism-Checker.git
    cd Free-Plagiarism-Checker
    ```

2. **Create a Virtual Environment**

    ```sh
    python -m venv venv
    ```

3. **Activate the Virtual Environment**

    - On **Windows**:

        ```sh
        venv\Scripts\activate
        ```

    - On **macOS/Linux**:

        ```sh
        source venv/bin/activate
        ```

4. **Install Dependencies**

    ```sh
    pip install -r requirements.txt
    ```

## Configuration

### Set Up Environment Variables

1. **Create a `.env` File**

    In the project root directory, create a file named `.env` and add your API keys:

    ```env
    API_KEY=your_api_key_here
    SEARCH_ENGINE_ID=your_search_engine_id_here
    ```

### Obtaining API Keys

To use the **Free Plagiarism Checker**, you need to obtain an API key and a Search Engine ID from Google Custom Search. Follow these steps to acquire them:

#### 1. Create a Google Cloud Project

- **Visit the Google Cloud Console:**

  [Google Cloud Console](https://console.cloud.google.com/)

- **Sign In:**

  Use your Google account to sign in. If you don't have one, you'll need to create it.

- **Create a New Project:**

  - Click on the project dropdown at the top of the page.
  - Select **"New Project"**.
  - Enter a **Project Name** (e.g., "PlagiarismChecker").
  - Click **"Create"**.

#### 2. Enable the Custom Search API

- **Navigate to APIs & Services:**

  From the left sidebar, go to **"APIs & Services"** > **"Library"**.

- **Search for Custom Search API:**

  In the search bar, type **"Custom Search API"**.

- **Enable the API:**

  Click on **"Custom Search API"** from the search results, then click **"Enable"**.

#### 3. Create API Credentials

- **Go to Credentials:**

  Within **"APIs & Services"**, click on **"Credentials"**.

- **Create Credentials:**

  - Click on **"Create Credentials"** > **"API Key"**.
  - A dialog will appear with your new **API Key**. Copy this key.

- **Restrict Your API Key (Recommended):**

  For security purposes, it's advisable to restrict your API key:

  - Click on **"Restrict Key"** in the dialog.
  - Under **"Application restrictions"**, select **"HTTP referrers"** or **"IP addresses"** based on your deployment.
  - Under **"API restrictions"**, select **"Restrict key"** and choose **"Custom Search API"**.
  - Click **"Save"**.

#### 4. Set Up a Custom Search Engine

- **Visit Google Custom Search Engine:**

  [Google Custom Search](https://cse.google.com/cse/all)

- **Create a New Search Engine:**

  - Click on **"Add"**.
  - In the **"Sites to search"** field, you can enter any website (e.g., `example.com`). This can be updated later to search the entire web.
  - Enter a **Search Engine Name** (e.g., "PlagiarismCheckerSearch").
  - Click **"Create"**.

- **Configure to Search the Entire Web:**

  - After creation, go to the **"Control Panel"** of your search engine.
  - Under **"Sites to search"**, click **"Edit"**.
  - Remove any specified sites to allow searching the entire web.
  - Save your changes.

- **Obtain the Search Engine ID:**

  - In the **"Control Panel"**, locate the **"Search engine ID"**. It will look something like `d285d5122c06b48c6`.
  - Copy this ID and add it to your `.env` file as `SEARCH_ENGINE_ID`.

#### 5. Finalize Configuration

- **Update the `.env` File:**

  Ensure your `.env` file contains the following with your obtained credentials:

    ```env
    API_KEY=your_api_key_here
    SEARCH_ENGINE_ID=your_search_engine_id_here
    ```

- **Verify API Access:**

  To ensure that your API key and Search Engine ID are working correctly, you can perform a test search using the Custom Search API.

## Usage

### Running the Script

Run the main script to perform plagiarism checking:

```sh
python main.py
```

This will generate `plagiarism_report.html` and `plagiarism_report.csv` in the project directory with the analysis results.

### Running in Visual Studio Code

1. **Open the Project in VS Code**

    ```sh
    code .
    ```

2. **Activate the Virtual Environment**

    Open the integrated terminal in VS Code and activate the virtual environment as per your operating system.

3. **Run the Script**

    - Press `F5` or navigate to the **Run and Debug** section and start the debugger.

## Project Structure

```
.
├── .env
├── .gitignore
├── main.py
├── requirements.txt
├── templates
│   └── report_template.html
├── plagiarism_report.html
└── plagiarism_report.csv
```

- **.env**: Stores environment variables like API keys.
- **.gitignore**: Specifies files and directories to be ignored by Git.
- **main.py**: Main application script.
- **requirements.txt**: Lists all project dependencies.
- **templates/report_template.html**: HTML template for generating plagiarism reports.
- **plagiarism_report.html**: Generated HTML report.
- **plagiarism_report.csv**: Generated CSV report.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [aiohttp](https://github.com/aio-libs/aiohttp)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [nltk](https://www.nltk.org/)
- [scikit-learn](https://scikit-learn.org/)
- [tqdm](https://github.com/tqdm/tqdm)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [Jinja2](https://jinja.palletsprojects.com/)
- [pandas](https://pandas.pydata.org/)

---
