from importlib import import_module
import spacy
from errant.annotator import Annotator
from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer
from camel_tools.tagger.default import DefaultTagger
from camel_tools.disambig.mle import MLEDisambiguator

# ERRANT version
__version__ = '2.2.2'

# Load an ERRANT Annotator object for a given language
def load(lang, nlp=None):
    # Make sure the language is supported
    supported = {"en", "ar"}
    if lang not in supported:
        raise Exception("%s is an unsupported or unknown language" % lang)

    if lang == "en":
        # Load spacy
        nlp = nlp or spacy.load(lang, disable=["ner"])

        # Load language edit merger
        merger = import_module("errant.%s.merger" % lang)

        # Load language edit classifier
        classifier = import_module("errant.%s.classifier" % lang)
        # The English classifier needs spacy
        classifier.nlp = nlp

        # Return a configured ERRANT annotator
        return Annotator(lang, nlp, merger, classifier)

    if lang == "ar":
        # Load spacy
        # nlp = nlp or spacy.load(lang, disable=["ner"])
        db = MorphologyDB.builtin_db()
        analyzer = Analyzer(db)
        mled = MLEDisambiguator.pretrained()
        tagger = DefaultTagger(mled, 'pos')
        nlp = [analyzer, tagger]

        # Load language edit merger
        merger = import_module("errant.%s.merger" % lang)

        # Load language edit classifier
        classifier = import_module("errant.%s.classifier" % lang)
        # The English classifier needs spacy
        #classifier.nlp = nlp

        # Return a configured ERRANT annotator
        return Annotator(lang, nlp, merger, classifier)