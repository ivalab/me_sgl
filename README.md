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
- [Results](#Results)
- [Perception](#Perception)
- [Goal Learning](#Goal-Learning)
- [Task Planning](#Task-Planning)
- [Execution](#Execution)
- [Scene Reconstruction](#Scene-Reconstruction)
- [Installation](#Installation)
- [Usage](#Usage)
- [Demo](#Demo)

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

# Results
Compared to the Table provided in the manuscript, this one includes further details for easy, medium, hard1 and hard2
scenarios.
![image](https://user-images.githubusercontent.com/27162640/165819616-4dc2fd2b-7f44-49a5-89cd-0b829e9774b2.png)


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

## Installation
1. Create a conda environment
```
conda create --name me_sgl python=3.6
```
2. Activate conda environment
```
conda activate me_sgl
```
3. Follow the official installation instruction, compile and build [downward](https://www.fast-downward.org/ObtainingAndRunningFastDownward)
4. The pretrained model for MaskRCNN requires specific version of pytorch, install pytorch via the following command:
```
conda install pytorch==1.9.0 torchvision==0.10.0 torchaudio==0.9.0 cudatoolkit=10.2 -c pytorch
```
5. Follow the installation instruction provided in [Symbolic Goal Learning](https://github.com/ivalab/mmf) without creating a new 
conda environment. You will also need to download the corresponding dataset which contains several dictionaries for decoding. 
6. Install all required libraries
```
pip install -r requirements.txt
```

## Usage
1. Download pretrained models for [MaskRCNN]() and the proposed [Symbolic Goal Learning](https://www.dropbox.com/home/IVALab/Project/STL/Opensource/Pretrained_models) network and put them under the folder of `pretrained_model`.  For symbolic goal learning model, you should download the one named resnet_bert_concat_sg_sts and uncompress it.
2. Taking the easy level task of cut task for example, the first step is to run symbolic goal learning approach to estimate the goal state for PDDL.
```
python mmf_cli/manipulation_experiment.py config=projects/resnet_bert_concat/configs/sgl/defaults_manipulation_experiment.yaml model=resnet_bert_concat dataset=sgl
```
If you'd like to evaluate other tasks or difficulty levels, you will need to modify the corresponding arguments in `defaults_manipulation_experiment.yaml`.
3. After predicting goal state for PDDL, to perform the manipulation in AI2THOR, run the following command:
For easy, medium or hard1 difficulties of cut task,
```
cd script
python cut_task_manipulation_experiment.py ../data --task_type cut_task --level easy
```
For hard2 difficulty of cut task,
```
cd script
python cut_task_manipulation_experiment_hard2.py ../data
```
It is similar to run experiments for other four tasks.

## Demo
![demo](https://user-images.githubusercontent.com/27162640/165842878-a4e75bd7-a87d-4754-9c07-da2ae00411ee.gif)

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

