| **Author**   | **Project** | **Documentation**                                                                   | **Build Status**              |
|:------------:|:-----------:|:-----------------------------------------------------------------------------------:|:-----------------------------:|
|   [**N. Curti**](https://github.com/Nico-Curti) <br/> [**E. Giampieri**](https://github.com/EnricoGiampieri)   |  **dermas**  | [![docs](https://img.shields.io/badge/documentation-latest-blue.svg?style=plastic)](https://github.com/eDIMESLab/dermas/blob/master/docs/usage.png) | **Linux/MacOS** : [![travis](https://travis-ci.com/eDIMESLab/dermas.svg?branch=master)](https://travis-ci.com/eDIMESLab/dermas) <br/> **Windows** : [![appveyor](https://ci.appveyor.com/api/projects/status/q1yvx7thoprqrsbo?svg=true)](https://ci.appveyor.com/project/Nico-Curti/dermas) |

[![GitHub pull-requests](https://img.shields.io/github/issues-pr/eDIMESLab/dermas.svg?style=plastic)](https://github.com/eDIMESLab/dermas/pulls)
[![GitHub issues](https://img.shields.io/github/issues/eDIMESLab/dermas.svg?style=plastic)](https://github.com/eDIMESLab/dermas/issues)

[![GitHub stars](https://img.shields.io/github/stars/eDIMESLab/dermas.svg?label=Stars&style=social)](https://github.com/eDIMESLab/dermas/stargazers)
[![GitHub watchers](https://img.shields.io/github/watchers/eDIMESLab/dermas.svg?label=Watch&style=social)](https://github.com/eDIMESLab/dermas/watchers)

<a href="https://github.com/eDIMESLab">
<div class="image">
<img src="https://cdn.rawgit.com/physycom/templates/697b327d/logo_unibo.png" width="90" height="90">
</div>
</a>

# Dermatological Melanoma Analysis and Segmentation - DERMAS

Histopathological image analyses for melanoma classification and segmentation.

The project has been developed in collaboration with the Sant'Orsola Hospital of Bologna and in particular with the Dermatological research group of this hospital.

1. [Installation](#installation)
2. [Authors](#authors)
3. [License](#license)
4. [Contributions](#contributions)
5. [Acknowledgments](#acknowledgments)
6. [Citation](#citation)


## Installation

First of all ensure that a right Python version is installed (Python >= 3.5 is required).
The [Anaconda/Miniconda](https://www.anaconda.com/) python version is recommended.

Download the project or the latest release:

```bash
git clone https://github.com/eDIMESLab/dermas
cd dermas
```

To install the prerequisites type:

```bash
pip install -r ./requirements.txt
```

In the `dermas` directory execute:

```bash
python setup.py install
```

or for installing in development mode:

```bash
python setup.py develop --user
```

## Usage

The project aims to analyze SVS images for the detection and classification of melanoma areas.
This package includes a pipeline of processing developed using `Snakemake` for a granular parallelization of the different tasks.

The `dermas` package includes multiple step of analysis:

- [`splitter.py`](https://github.com/eDIMESLab/dermas/blob/master/SlideSeg/splitter.py): starting from a set of manually annotated SVS images, the first step is the generation of the dataset into a series of patches (original patch + annotated patch).
This step was developed starting from the [`SlideSeg`](https://github.com/btcrabb/SlideSeg) Python package with some reviews and optimizations.
Using the `splitter.py` file we unpack each level of a given SVS image (original image) into a series of patches.
Associated to the SVS image an annotation file must be provided in format .xml (or .roi if you use old version of Seeden Viewer for the annotations).
The .xml file (annotated image) creates the corresponding annotated patches.
For sake of storage minimization we save only patches which include a signal (at least on pixel of the annotated part).

- [`refine_mask.py`](https://github.com/eDIMESLab/dermas/blob/master/SlideSeg/refine_mask.py): each saved patch is re-processed to refine the annotated mask and exclude artifacts or incorrect labels.
NOTE: pay attention to the COLORS variable at the beginning of this script! It defines the series of valid colors. Each color not included in this list is associated to the nearest one of them.

- [`counting_mask.py`](https://github.com/eDIMESLab/dermas/blob/master/SlideSeg/counting_mask.py): count the labels found in each patch and generate a useful database.
To each patch filename we save a boolean list of the included colors (1 if there is a color and 0 otherwise).
In this way we can use this generated database to perform the next analyses only on the subset of interest.

All these steps can be run into a sequential pipeline using the [`derma_pipeline.sh`](https://github.com/eDIMESLab/dermas/blob/master/derma_pipeline.sh) (for MacOS/Linux users) and [`derma_pipeline.ps1`](https://github.com/eDIMESLab/dermas/blob/master/derma_pipeline.ps1) (for Windows users).

```bash
./derma_pipeline.sh ./slices/ ./labels/
```

We encourage to perform all the analyses using the provided [`Snakefile`](https://github.com/eDIMESLab/dermas/blob/master/pipeline/Snakefile).
In this way all the described above steps are performed in the most efficient way.
Moreover we can parallelize our pipeline to the full series of available images/annotations.
Before use it take care to modify the [`config.yaml`](https://github.com/eDIMESLab/dermas/blob/master/pipeline/config.yaml) according to your needs and **your folders tree**.

Example:

```bash
snakemake -j32
```

an example of the Snakefile workflow can be seen [here](https://github.com/eDIMESLab/dermas/blob/master/docs/workflow.pdf)


## Authors

* **Enrico Giampieri** [git](https://github.com/EnricoGiampieri), [unibo](https://www.unibo.it/sitoweb/enrico.giampieri)
* **Nico Curti** [git](https://github.com/Nico-Curti), [unibo](https://www.unibo.it/sitoweb/nico.curti2)

See also the list of [contributors](https://github.com/eDIMESLab/dermas/contributors) [![GitHub contributors](https://img.shields.io/github/contributors/eDIMESLab/dermas.svg?style=plastic)](https://github.com/eDIMESLab/dermas/graphs/contributors/) who participated in this project.

## License

The `dermas` package is licensed under the MIT "Expat" License. [![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/eDIMESLab/dermas/blob/master/LICENSE.md)


### Contributions

Any contribution is more than welcome. Just fill an issue or a pull request and I will check ASAP!

If you want update the list of layer objects please pay attention to the syntax of the layer class and to the names of member functions/variables used to prevent the compatibility with other layers and utility functions.


### Acknowledgments

Thanks goes to all contributors of this project.

### Citation

Please cite `dermas` if you use it in your research.

```tex
@misc{dermas,
  author = {Enrico Giampieri and Nico Curti},
  title = {Dermatological Melanoma Analysis and Segmentation},
  year = {2019},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/eDIMESLab/dermas}},
}
```

