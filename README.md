# LLM-demo

## About

Welcome to **LLM-demo**, a Gradio based Multi-LLMs Agent, created for HCI-lab02.
The author is Zixun Huang and the agent can help users access different agents at the same time.
The users can easily compare different answers to their questions and choose the best one.

## Installation

To install **LLM-demo**, all that needs to be done is clone this repository to the desired directory.

### Dependencies

**LLM-demo** uses [Anaconda](https://www.anaconda.com/distribution/) to manage Python and it's dependencies, listed in [`environment.yml`](environment.yml). To install the `py312` Python environment, set up Anaconda (or Miniconda), then download the environment dependencies with:

```shell
conda env create -f environment.yml
```

## Usage

Before using the repository, make sure to activate the `py312` environment with:

```shell
conda activate py312
```

### Run

Create .env file to store the api keys.
Run [`demo.py`](demo.py) from the repository's root directory:

```shell
python demo.py
```

If you have any questions, please feel free to contact Zixun Huang(2153679@mail.tongji.edu.cn)
