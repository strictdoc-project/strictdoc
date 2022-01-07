class Strictdoc < Formula
  include Language::Python::Virtualenv

  desc "Software for writing technical requirements specifications."
  homepage "https://github.com/stanislaw/strictdoc"
  url "https://files.pythonhosted.org/packages/b9/07/f0c348e6b255d29ece30ab24e51eb86f6dbd3b9bc5e22e321445c144bc26/strictdoc-0.0.18.tar.gz"
  sha256 "c5a33ca63d14f9a81b2490d118bda1f1f5a38038abfb22b18662c0c46fe2d1fb"
  license "Apache-2.0"

  depends_on "python3"

  resource "Arpeggio" do
    url "https://files.pythonhosted.org/packages/8d/4b/042f027e6b818350f4863509884559f0fc744df8c5c36f4a084511b9457a/Arpeggio-1.10.2.tar.gz"
    sha256 "bfe349f252f82f82d84cb886f1d5081d1a31451e6045275e9f90b65d0daa06f1"
  end

  resource "beautifulsoup4" do
    url "https://files.pythonhosted.org/packages/a1/69/daeee6d8f22c997e522cdbeb59641c4d31ab120aba0f2c799500f7456b7e/beautifulsoup4-4.10.0.tar.gz"
    sha256 "c23ad23c521d818955a4151a67d81580319d4bf548d3d49f4223ae041ff98891"
  end

  resource "docutils" do
    url "https://files.pythonhosted.org/packages/2f/e0/3d435b34abd2d62e8206171892f174b180cd37b09d57b924ca5c2ef2219d/docutils-0.16.tar.gz"
    sha256 "c2de3a60e9e7d07be26b7f2b00ca0309c207e06c100f9cc2a94931fc75a478fc"
  end

  resource "Jinja2" do
    url "https://files.pythonhosted.org/packages/4f/e7/65300e6b32e69768ded990494809106f87da1d436418d5f1367ed3966fd7/Jinja2-2.11.3.tar.gz"
    sha256 "a6d58433de0ae800347cab1fa3043cebbabe8baa9d29e668f1c768cb87a333c6"
  end

  resource "lxml" do
    url "https://files.pythonhosted.org/packages/84/74/4a97db45381316cd6e7d4b1eb707d7f60d38cb2985b5dfd7251a340404da/lxml-4.7.1.tar.gz"
    sha256 "a1613838aa6b89af4ba10a0f3a972836128801ed008078f8c1244e65958f1b24"
  end

  resource "MarkupSafe" do
    url "https://files.pythonhosted.org/packages/bf/10/ff66fea6d1788c458663a84d88787bae15d45daa16f6b3ef33322a51fc7e/MarkupSafe-2.0.1.tar.gz"
    sha256 "594c67807fb16238b30c44bdf74f36c02cdf22d1c8cda91ef8a0ed8dabf5620a"
  end

  resource "Pygments" do
    url "https://files.pythonhosted.org/packages/94/9c/cb656d06950268155f46d4f6ce25d7ffc51a0da47eadf1b164bbf23b718b/Pygments-2.11.2.tar.gz"
    sha256 "4e426f72023d88d03b2fa258de560726ce890ff3b630f88c21cbb8b2503b8c6a"
  end

  resource "python-datauri" do
    url "https://files.pythonhosted.org/packages/25/dd/c44f6d9c46b0755f5888223df64b2a913c8fb6960e2353fd465e6bfefcb1/python-datauri-0.2.9.tar.gz"
    sha256 "3a23f135b5b029cf4f4b8e91d50d537b8398b07291872b6bbda7d62254faeaea"
  end

  resource "reqif" do
    url "https://files.pythonhosted.org/packages/1b/21/d0ccefe9b980dc45a8e21f4899861af44d436c2cfd9609e9461488c2d8c0/reqif-0.0.2.tar.gz"
    sha256 "2bcc3c37a1b8221c697f9d2a65a91db5a6ac93f94435409c5561076bd511f2be"
  end

  resource "soupsieve" do
    url "https://files.pythonhosted.org/packages/e1/25/a3005eedafb34e1258458e8a4b94900a60a41a2b4e459e0e19631648a2a0/soupsieve-2.3.1.tar.gz"
    sha256 "b8d49b1cd4f037c7082a9683dfa1801aa2597fb11c3a1155b7a5b94829b4f1f9"
  end

  resource "textX" do
    url "https://files.pythonhosted.org/packages/e3/6e/775e86f7d6ef22bf32999a73479d55cc93869b80af8088b8225c2d8a2cd0/textX-2.3.0.tar.gz"
    sha256 "265afc12d4ae421a7794c8cdc58c6eed44cc879f078cb54c32d5dc6bc74efbac"
  end

  resource "XlsxWriter" do
    url "https://files.pythonhosted.org/packages/15/72/75b6c904ebabb3fc22965dd78e080252d5950af652a34cd3e0ed538ab1ff/XlsxWriter-1.4.5.tar.gz"
    sha256 "0956747859567ec01907e561a7d8413de18a7aae36860f979f9da52b9d58bc19"
  end

  def install
    virtualenv_create(libexec, "python3")
    virtualenv_install_with_resources
  end

end
