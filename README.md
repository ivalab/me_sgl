# Manipulation Experiment
Manipulation Experiment for Symbolic Goal Learning in a Hybrid, Modular Framework for Human Instruction Following. The proposed
hybrid, modular framework consists of **Perception**, **Goal Learning**, **Task Planning** and **Execution** modules. 
The **Perception** module is responsible for interpreting visual information of surrounding environments.
The **Goal Learning** module learns symbolic goal representation for the **Task Planning** module.
The **Task Planning** module generates a sequence of low-level actions. 
The **Execution** module performs generated actions with operational information detected by the **Perception** module.

## Table of Contents
- [Perception](#Perception)
- [Goal Learning](#Goal-Learning)
- [Task Planning](#Task-Planning)
- [Execution](#Execution)
- [Data](#Data)

## Perception
We employ Mask R-CNN as the Perception module to detect objects and their category segmentation masks. 
The categorical information is detected and corresponding affordances and attributes are retrieved from knowledge base to build
the initial state for PDDL.

**Installation**

## Goal Learning
[Symbolic Goal Learning](https://github.com/ivalab/mmf) via vision and language is proposed and employed for learning goal state representation for PDDL. 
For installation, please refer to the repository for our work.

## Task Planning
The Task Planner module is a PDDL planner that outputs a primitive action sequence from the detected 
initial and goal states, which is then sent to the robot for execution.
For installation, please refer to [Fast Downward](https://github.com/aibasel/downward).

## Execution
Manipulation experiments are conducted in the simulator [AI2THOR](https://ai2thor.allenai.org/).
Given that AI2THOR does not support physical modeling of robot-object interaction, masks which are provided via Pereception module
is served as operational information.

**Installation**

## Data


## Usage

## Citation
If you'd like to compare against this work, please cite:

```bibtex
@article{xu2022sgl,
  title={SGL: Symbolic Goal Learning for Human Instruction Following in Robot Manipulation},
  author={Xu, Ruinian and Chen, Hongyi and Lin, Yunzhi, and Vela, Patricio A},
  journal={arXiv preprint arXiv:2202.12912},
  year={2022}
}
```
