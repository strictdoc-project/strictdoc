# Create `brew` formula

One cannot setup the `venv` using poetry cause [`poetry` does not allow to install stictdoc in development mode yet](https://github.com/python-poetry/poetry/issues/34).
[Create and activate a `venv` the plain Python way](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments) instead.

```
python3 -m venv venv-strictdoc-homebrew
source venv-strictdoc-homebrew/bin/activate
```

Install `brew` on Mac OS or Linux (on Linux into `/home/linuxbrew/.linuxbrew/bin/brew`) like [described on the website](https://brew.sh/).

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Install `strictdoc` and the homebrew helper `poet` for generating Python formulas into the `venv`:

    pip install strictdoc homebrew-pypi-poet

Generate the Homebrew formula for `strictdoc` including it's dependencies and leave the `venv`:

    poet -f strictdoc > Formula/strictdoc.rb
    deactivate

Adjust the content of `Formula/strictdoc.rb`.

# Install `strictdoc` via `brew`

When [adding `strictdoc-project/strictdoc` as formula source](https://docs.brew.sh/Taps) with

    brew tap strictdoc-project/strictdoc

will show something like this:

    ==> Tapping strictdoc-project/strictdoc
    Cloning into '/home/linuxbrew/.linuxbrew/Homebrew/Library/Taps/strictdoc-project/homebrew-strictdoc'...

Installation:

    brew install strictdoc-project/strictdoc
