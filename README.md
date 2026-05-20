<div align="center">
    <h1 align="center">experimental.doodle</h1>
</div>
<div align="center">
[![PyPI](https://img.shields.io/pypi/v/experimental.doodle)](https://pypi.org/project/experimental.doodle/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/experimental.doodle)](https://pypi.org/project/experimental.doodle/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/experimental.doodle)](https://pypi.org/project/experimental.doodle/)
[![PyPI - License](https://img.shields.io/pypi/l/experimental.doodle)](https://pypi.org/project/experimental.doodle/)
[![PyPI - Status](https://img.shields.io/pypi/status/experimental.doodle)](https://pypi.org/project/experimental.doodle/)


[![PyPI - Plone Versions](https://img.shields.io/pypi/frameworkversions/plone/experimental.doodle)](https://pypi.org/project/experimental.doodle/)

[![CI](https://github.com/collective/experimental.doodle/actions/workflows/main.yml/badge.svg)](https://github.com/collective/experimental.doodle/actions/workflows/main.yml)
![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000)

[![GitHub contributors](https://img.shields.io/github/contributors/collective/experimental.doodle)](https://github.com/collective/experimental.doodle)
[![GitHub Repo stars](https://img.shields.io/github/stars/collective/experimental.doodle?style=social)](https://github.com/collective/experimental.doodle)

</div>

A new addon for Plone that should behave like doodle.
This is an experimental package, used for an exercise.

## Features

TODO: replace doodle.

## Exercise instructions

```shell
$ git clone git@github.com:syslabcom/experimental.doodle.git
$ make start
```


## Plonex instructions

You need the latest source version of `plonex` for this to work,

```shell
$ plonex dependencies
$ plonex supervisor start
$ plonex adduser admin admin
$ plonex runwsgi
```

## Installation

Install experimental.doodle with `pip`:

```shell
pip install experimental.doodle
```

And to create the Plone site:

```shell
make create-site
```

## Contribute

- [Issue tracker](https://github.com/collective/experimental.doodle/issues)
- [Source code](https://github.com/collective/experimental.doodle/)

### Prerequisites ✅

-   An [operating system](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation) that runs all the requirements mentioned.
-   [uv](https://6.docs.plone.org/install/create-project-cookieplone.html#uv)
-   [Make](https://6.docs.plone.org/install/create-project-cookieplone.html#make)
-   [Git](https://6.docs.plone.org/install/create-project-cookieplone.html#git)
-   [Docker](https://docs.docker.com/get-started/get-docker/) (optional)

### Installation 🔧

1.  Clone this repository, then change your working directory.

    ```shell
    git clone git@github.com:collective/experimental.doodle.git
    cd experimental.doodle
    ```

2.  Install this code base.

    ```shell
    make install
    ```


### Add features using `plonecli` or `bobtemplates.plone`

This package provides markers as strings (`<!-- extra stuff goes here -->`) that are compatible with [`plonecli`](https://github.com/plone/plonecli) and [`bobtemplates.plone`](https://github.com/plone/bobtemplates.plone).
These markers act as hooks to add all kinds of subtemplates, including behaviors, control panels, upgrade steps, or other subtemplates from `plonecli`.

To run `plonecli` with configuration to target this package, run the following command.

```shell
make add <template_name>
```

For example, you can add a content type to your package with the following command.

```shell
make add content_type
```

You can add a behavior with the following command.

```shell
make add behavior
```

```{seealso}
You can check the list of available subtemplates in the [`bobtemplates.plone` `README.md` file](https://github.com/plone/bobtemplates.plone/?tab=readme-ov-file#provided-subtemplates).
See also the documentation of [Mockup and Patternslib](https://6.docs.plone.org/classic-ui/mockup.html) for how to build the UI toolkit for Classic UI.
```

## License

The project is licensed under GPLv2.

## Credits and acknowledgements 🙏

Generated using [Cookieplone (1.0.0)](https://github.com/plone/cookieplone) and [cookieplone-templates (f436000)](https://github.com/plone/cookieplone-templates/commit/f43600068a2ed0e833072cdc4963358a238a430a) on 2026-05-20 08:27:06.781515. A special thanks to all contributors and supporters!
