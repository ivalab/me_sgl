# Manipulation Experiment
Manipulation Experiment for Symbolic Goal Learning in a Hybrid, Modular Framework for Human Instruction Following. The proposed
hybrid, modular framework consists of **Perception**, **Goal Learning**, **Task Planning** and **Execution** modules. 
The **Perception** module is responsible for interpreting visual information of surrounding environments.
The **Goal Learning** module learns symbolic goal representation for the **Task Planning** module.
The **Task Planning** module generates a sequence of low-level actions. 
The **Execution** module performs generated actions with operational information detected by the **Perception** module.

## Table of Contents
- [Experimental Setup](#Experimental-Setup)
- [Evaluation Metrics](#Evaluation-Metrics)
- [Perception](#Perception)
- [Goal Learning](#Goal-Learning)
- [Task Planning](#Task-Planning)
- [Execution](#Execution)
- [Scene Reconstruction](#Scene-Reconstruction)
- [Installation](#Installation)
- [Usage](#Usage)

## Experimental Setup
Five different daily activities are conducted, which include Picking and Placing, Object Delivery, Cutting, Cleaning and Cooking. 
There are four different levels of scenarios for each task. Easy scenario only contains involved objects in the scene. 
Medium scenario incorporates irrelevant objects. The first hard scenario further includes multiple candidates while 
the second hard scenario misses partial or all objects required to perform the task. 
Due to missing objects in the scene, task planning is not expected to find valid solutions and execution is also not required for
the second hard case. There are 10 scenarios for each level and either novel instruction or intent will be paired with the image.

## Evaluation Metrics
To evaluate each module in the instruction following framework, each manipulation experiment trial is considered as
successful if it satifies four conditions. 
For **Perception**, all involved objects are required to be correctly detected, which constructs the initial state for PDDL. 
For **Goal Learning**, PDDL goal state should be correctly predicted. 
For **Task Planning**, generated action sequence is composed of correct ordered actions. 
Given that AI2THOR does not support physical modeling of robot-object interaction, **Execution** evaluation requires 
the Intersection-of-Union (IoU) of detected and ground-truth masks for objects to be over the 0.5 threshold.

## Perception
We employ [Mask R-CNN](https://arxiv.org/abs/1703.06870) as the Perception module to detect objects and their category segmentation masks. 
The categorical information is detected and corresponding affordances and attributes are retrieved from knowledge base to build
the initial state for PDDL.
The initial state of PDDL consists of listed objects with corresponding predicates which could be affordance or attribute. 

## Goal Learning
[Symbolic Goal Learning](https://github.com/ivalab/mmf) via vision and language is proposed and employed for learning 
goal state representation for PDDL. 
This goal learning network consists of visual and linguistic encoders, multi-modal fusion and classification modules.
The visual encoder processes input image and outputs visual features.
The linguistic encoder takes a sentence of natural langauge as input and outputs linguistic features.
Multi-modal fusion module is responsible for jointly fusing visual and linguistic features into the same domain. 
The classification module produces predictions of symbolic representations for PDDL via joint features.

## Task Planning
For task planning, we employ the Planning Domain Def-
inition Language (PDDL), a widely used symbolic planning
language. With a list of pre-defined objects and their corre-
sponding predicates (such as dirty, graspable, etc.), a domain
consists of primitive actions and corresponding effects. Here,
affordances and attributes serve to define available predicates
for subsequently specifying object-action-object relationships.
Planning requires establishing a problem, which is composed
of the initial state and a desired goal state of the world. The
initial state is formed with a list of objects with corresponding
predicates. The goal state is structured in the form of action,
subject and object. From the domain and problem specifica-
tion, a PDDL planner produces a sequence of primitive actions
leaving the world in the goal state when executed.
[Fast Downward](https://github.com/aibasel/downward) is employed in this module.

## Execution
Manipulation experiments are conducted in the simulator [AI2THOR](https://ai2thor.allenai.org/).
Given that AI2THOR does not support physical modeling of robot-object interaction, masks which are provided via Pereception module
is served as operational information.

## Scene Reconstruction
For each experimental sample, it consists of a text file saves natural language input, a RGB image, a json file stores all information 
for recovering environmental setup and a text file saves ground-truth PDDL goal state. All experiment samples are stored in the ```data```
folder.

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
