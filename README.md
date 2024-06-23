# VisioNomicon

VisioNomicon is a powerful Python-based command-line utility tool designed to rename image files using the capabilities of GPT-4o. Descriptive filenames are generated based on a user given template and the content of the image.

![demo][DEMO]

## Features

- Rename image files based on generated filenames from GPT-4V
- Flexible name generation based on user given structure
- Ability to create a mapping file for renamed images
- Execute renaming based on a generated mapping file
- Undo renaming to revert to original filenames
- Verification step for generated names using GPT-4o
- Support for multiple retry attempts in case of validation or errors
- Supported file types: `.png`, `.jpeg`, `.jpg`, `.webp`, `.gif` (non-animated)

## Prerequisites

- Python 3.6+
- Access to OpenAI API with GPT-4o capabilities (API key required)

## Installation

You can install the package using pip via the following command:

```bash
pip install VisioNomicon
```

Alternatively, you can manually install the package by downloading the source distribution and running the following commands:

1. Download the latest source distribution from the [Releases](https://github.com/rehanzo/VisioNomicon/releases) page.
2. Extract the file and navigate to the extracted directory.
3. Run the following command to install:

```bash
pip install .
```

## Usage

To use VisioNomicon, you need to set the `OPENAI_API_KEY` environment variable to your OpenAI API key. This can generally be done with a command like the following:
```bash
export OPENAI_API_KEY='your_api_key_here'
```

Run the script with the desired flags and arguments:

```bash
VisioNomicon [OPTIONS]
```

Or in one single command:

```bash
OPENAI_API_KEY='your_api_key_here' VisioNomicon [OPTIONS] 
```

### Options

- `-f`, `--files`: Specify file paths of the images to create mapping for
- `-o`, `--output`: Specify a JSON mapping file to be created with original and new file paths. Defaults to `$XDG_DATA_HOME/visionomicon/mapping-%Y-%m-%d-%H-%M-%S.json`
- `-x`, `--execute`: Execute renaming based on existing mapping file. Calling this without a value uses the most recently created mapping in `$XDG_DATA_HOME/visionomicon`
- `-ox`, `--mapex`: Map and execute renaming in one step
- `-u`, `--undo`: Revert renaming to original filenames using a mapping file. Calling this without a value uses the most recently created mapping in `$XDG_DATA_HOME/visionomicon`
  - It is important to note, if the file names or locations change after executing a mapping, you will not be able to undo
- `-t`, `--template`: Define the template for renaming image files, without file extension. It is recommended to use square brackets to define elements of the filename. Defaults to `[SubjectDescription]\_[MainColor/ColorScheme]\_[StyleOrFeel]\_[CompositionElement]`
- `-e`, `--validation-retries`: Specify the number of retries for name validation (defaults to 3)
- `-v`, `--error-retries`: Specify the number of retries in case of OpenAI errors (defaults to 3)
- `-E`, `--ignore-validation-fail`: If validation retries limit is reached, map file to original name instead of returning an error
- `-V`, `--ignore-error-fail`: If error retries limit is reached, map file to original name instead of returning an error
- `-b`, `--create-batch`: Create batch job through OpenAI API.
- `-B`, `--retrieve-batch`: Retrieve batch job output through OpenAI API. Run this 24 hours after creating the batch job.

### Example Commands

```bash
VisioNomicon -f image1.jpg image2.png -ox
```

This is the most straightforward usage. A mapping file is created for the images, placed at the default location (`$XDG_DATA_HOME/visionomicon/mapping-%Y-%m-%d-%H-%M-%S.json`). Immediately afterwards, this file is executed, renaming the files.

```bash
VisioNomicon -f image1.jpg image2.png -o mapping.json -t "[Object]_[Color]_[Style]"
```

This command will create a rename mapping file for `image1.jpg` and `image2.png` based on the provided template and output the mapping to `mapping.json`.

Subsequently, you can execute the mapping, renaming the files.

```bash
VisioNomicon -x mapping.json
```

This can also be done in one single command if you'd like, using `-ox`:

```bash
VisioNomicon -f image1.jpg image2.png -ox mapping.json -t "[Object]_[Color]_[Style]"
```

## Limitations

- GPT-4o is limited in the file types it can handle(.png, .jpeg, .jpg, .webp, non-animated .gif), and the size (up to 20MB)
- With some templates it can be quite finicky, not really generating the filenames you might expect

## Contributing

Contributions are welcome. Please open an issue first to discuss what you would like to change or add.

## License

This project is open-sourced under the [GLP-3.0 License](LICENSE).

## Disclaimer

This tool is not affiliated with OpenAI. The functionality is subject to change based on updates to the API or the terms of service provided by OpenAI.

[DEMO]: https://raw.githubusercontent.com/rehanzo/VisioNomicon/master/assets/demonstration.gif 
