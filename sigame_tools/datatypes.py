from __future__ import annotations

import json
import shutil
from typing import List, Iterator, Any, Dict, Type
from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from xml.dom.minidom import parse, Document, Element, Text
from zipfile import ZipFile

from sigame_tools import helper


class JSONSerializeable(ABC):
    @abstractmethod
    def json_serialize(self) -> Dict[str, Any]:
        pass

    @classmethod
    @abstractmethod
    def json_deserialize(cls, d: Dict[str, Any]) -> None | JSONSerializeable:
        return None


class XMLOp(ABC):
    @abstractmethod
    def read_xml(self, el: Element) -> None:
        pass

    @abstractmethod
    def write_xml(self, root: Document) -> None | Element:
        pass


class Named:
    def __init__(self, name: str = "") -> None:
        super(Named, self).__init__()
        self.name: str = name


class Info:
    def __init__(self):
        super(Info, self).__init__()
        self.__authors: List[str] = []
        self.__sources: List[str] = []
        self.comments: str = ""

    @property
    def authors(self):
        return self.__authors

    @property
    def sources(self):
        return self.__sources


class InfoOwner(Named, JSONSerializeable, XMLOp):
    def __init__(self, name: str = ""):
        super().__init__(name=name)
        self.__info: Info = Info()

    @property
    def info(self):
        return self.__info

    def copy_info(self, other: InfoOwner):
        self.__info = other.info

    def json_serialize(self) -> Dict[str, Any]:
        # if self.info.authors or self.info.sources or self.info.comments:
        info = {}
        if self.info.authors:
            info["authors"] = self.info.authors
        if self.info.sources:
            info["sources"] = self.info.sources
        if self.info.comments:
            info["comments"] = self.info.comments
        return info

    @classmethod
    def json_deserialize(cls, d: Dict[str, Any]) -> None | InfoOwner:
        if "info" not in d:
            return None
        d_info = d["info"]
        if not ("authors" in d_info or "sources" in d_info or "comments" in d_info):
            return None
        i = InfoOwner()
        i.info.authors.extend(d_info.get("authors", []))
        i.info.sources.extend(d_info.get("sources", []))
        i.info.comments = d_info.get("comments", "")
        return i

    def read_xml(self, el: Element):
        assert el.nodeName == "info"
        el_authors_l: List[Element] = el.getElementsByTagName("authors")
        if el_authors_l:
            el_author_l: List[Element] = el_authors_l[0].getElementsByTagName("author")
            for el_author in el_author_l:
                self.info.authors.append(helper.get_text(el_author))
        el_sources_l: List[Element] = el.getElementsByTagName("sources")
        if el_sources_l:
            el_source_l: List[Element] = el_sources_l[0].getElementsByTagName("source")
            for el_source in el_source_l:
                self.info.sources.append(helper.get_text(el_source))
        el_comments_l: List[Element] = el.getElementsByTagName("comments")
        if el_comments_l:
            # el_comment_l: Text = el_comments_l[0].childNodes[0]
            # self.info.comments = el_comment_l.data
            self.info.comments = helper.get_text(el_comments_l[0])

    def write_xml(self, root: Document) -> None | Element:
        if not (self.info.authors or self.info.sources or self.info.comments):
            return None
        el: Element = root.createElement("info")
        if self.info.authors:
            el_authors: Element = root.createElement("authors")
            for author in self.info.authors:
                el_author: Element = root.createElement("author")
                if author:
                    el_author.appendChild(root.createTextNode(author))
                el_authors.appendChild(el_author)
            el.appendChild(el_authors)
        if self.info.sources:
            el_sources: Element = root.createElement("sources")
            for source in self.info.sources:
                el_source: Element = root.createElement("source")
                if source:
                    el_source.appendChild(root.createTextNode(source))
                el_sources.appendChild(el_source)
            el.appendChild(el_sources)
        if self.info.comments:
            el_comments: Element = root.createElement("comments")
            el_comments.appendChild(root.createTextNode(self.info.comments))
            # el_comments: Element = root.tex("comments")
            el.appendChild(el_comments)
        return el


class Package(InfoOwner, JSONSerializeable, XMLOp):
    """
    Based on https://github.com/VladimirKhil/SI/blob/master/src/Common/SIPackages/Package.cs
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.version = 4.0
        self.id = ""
        self.restriction = ""
        self.publisher = ""
        self.difficulty = 5
        self.logo = ""
        self.date = ""
        self.language = ""
        self.__tags: List[str] = []
        self.__rounds: List[Round] = []

    @property
    def rounds(self):
        return self.__rounds

    @property
    def tags(self):
        return self.__tags

    @classmethod
    def from_document(cls, doc: Document) -> Package:
        root: Element = doc.documentElement
        pac: Package = Package()
        pac.read_xml(root)
        return pac

    def json_serialize(self):
        res = {
            # "package": "http://vladimirkhil.com/ygpackage3.0.xsd",
            "name": self.name,
            "version": self.version,
            "id": self.id,
            "difficulty": self.difficulty,
            "rounds": self.rounds
        }
        info = super(Package, self).json_serialize()
        if info:
            res["info"] = info
        if self.restriction:
            res["restriction"] = self.restriction
        if self.date:
            res["date"] = self.date
        if self.publisher:
            res["publisher"] = self.publisher
        if self.logo:
            res["logo"] = self.logo
        if self.date:
            res["date"] = self.date
        if self.language:
            res["language"] = self.language
        if self.tags:
            res["tags"] = self.tags
        return res

    @classmethod
    def json_deserialize(cls, d) -> None | Package:
        if "rounds" not in d:
            return None
        print(d)
        p = Package(d["name"])
        io = super().json_deserialize(d)
        if io:
            p.copy_info(io)
        p.version = d.get("version", p.version)
        p.id = d.get("id", p.id)
        p.restriction = d.get("restriction", p.restriction)
        p.publisher = d.get("publisher", p.publisher)
        p.difficulty = d.get("difficulty", p.difficulty)
        p.logo = d.get("logo", p.logo)
        p.date = d.get("date", p.date)
        p.language = d.get("language", p.language)
        p.rounds.clear()
        p.rounds.extend(d["rounds"])
        p.tags.clear()
        p.tags.extend(d.get("tags", []))
        return p

    def read_xml(self, el: Element):
        assert el.nodeName == "package"

        self.name = el.getAttribute("name")
        self.version = float(el.getAttribute("version") or self.version)
        self.id = el.getAttribute("id")
        self.restriction = el.getAttribute("restriction")
        self.date = el.getAttribute("date")
        self.publisher = el.getAttribute("publisher")
        self.difficulty = int(el.getAttribute("difficulty") or self.difficulty)
        self.logo = el.getAttribute("logo")
        self.language = el.getAttribute("language")

        el_info_l: List[Element] = el.getElementsByTagName("info")
        if el_info_l and el_info_l[0] in el.childNodes:
            super(Package, self).read_xml(el_info_l[0])

        el_tags: List[Element] = el.getElementsByTagName("tags")
        if el_tags:
            el_tag: Element
            for el_tag in el_tags[0].getElementsByTagName("tag"):
                self.tags.append(helper.get_text(el_tag))
        # rounds: Element = el.getElementsByTagName("rounds")[0]
        # el_round: Element
        for el_round in el.getElementsByTagName("round"):
            _round = Round()
            _round.read_xml(el_round)
            self.rounds.append(_round)

    def write_xml(self, root: Document) -> Element:
        el: Element = root.createElement("package")
        el.setAttribute("xmlns", "http://vladimirkhil.com/ygpackage3.0.xsd")
        el.setAttribute("name", self.name)
        el.setAttribute("version", f"{self.version:g}")
        if self.id:
            el.setAttribute("id", self.id)
        if self.restriction:
            el.setAttribute("restriction", self.restriction)
        if self.date:
            el.setAttribute("date", self.date)
        if self.publisher:
            el.setAttribute("publisher", self.publisher)
        if self.difficulty:
            el.setAttribute("difficulty", str(self.difficulty))
        if self.logo:
            el.setAttribute("logo", self.logo)
        if self.language:
            el.setAttribute("language", self.language)

        if self.tags:
            el_tags: Element = root.createElement("tags")
            for tag in self.tags:
                el_tag: Element = root.createElement("tag")
                el_tag.appendChild(root.createTextNode(tag))
                el_tags.appendChild(el_tag)
            el.appendChild(el_tags)

        el_info = super(Package, self).write_xml(root)
        if el_info:
            el.appendChild(el_info)

        if self.rounds:
            el_rounds = root.createElement("rounds")
            el.appendChild(el_rounds)
            for p_round in self.rounds:
                el_round = p_round.write_xml(root)
                el_rounds.appendChild(el_round)

        return el

    def __repr__(self) -> str:
        return f"SIGame Package {self.name}, authors: {', '.join(self.info.authors)}, num of rounds: {len(self.rounds)}"

    # def add_author(self, author : str):
    #     self.authors.append(author)


class Round(InfoOwner, JSONSerializeable, XMLOp):
    def __init__(self, name: str = "", final=False) -> None:
        super().__init__(name)
        self.final: bool = final
        self.themes: List[Theme] = []

    def json_serialize(self):
        res = {
            "name": self.name,
            "themes": self.themes
        }
        info = super(Round, self).json_serialize()
        if info:
            res["info"] = info
        if self.final:
            res["final"] = True
        return res

    @classmethod
    def json_deserialize(cls, d) -> None | Round:
        if "themes" not in d:
            return None
        r = Round(d["name"], d.get("final", False))
        io = super().json_deserialize(d)
        if io:
            r.copy_info(io)
        r.themes.extend(d["themes"])
        return r

    def read_xml(self, el: Element) -> None:
        assert el.nodeName == "round"
        self.name = el.getAttribute("name")
        r_type = el.getAttribute("type")
        self.final = r_type == "final"

        el_info_l: List[Element] = el.getElementsByTagName("info")
        if el_info_l and el_info_l[0] in el.childNodes:
            super(Round, self).read_xml(el_info_l[0])

        for el_theme in el.getElementsByTagName("theme"):
            theme = Theme()
            theme.read_xml(el_theme)
            self.themes.append(theme)

    def write_xml(self, root: Document) -> Element:
        el: Element = root.createElement("round")
        el.setAttribute("name", self.name)
        if self.final:
            el.setAttribute("type", "final")

        el_info = super(Round, self).write_xml(root)
        if el_info:
            el.appendChild(el_info)

        if self.themes:
            el_themes = root.createElement("themes")
            el.appendChild(el_themes)
            for theme in self.themes:
                el_theme = theme.write_xml(root)
                el_themes.appendChild(el_theme)

        return el

    def __repr__(self) -> str:
        return f"SIGame Round: \"{self.name}\"{' (final round)' if self.final else ''}, themes: {len(self.themes)}"


class Theme(InfoOwner, JSONSerializeable, XMLOp):
    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.questions: List[Question] = []

    def json_serialize(self):
        res = {
            "name": self.name,
            "questions": self.questions
        }
        info = super(Theme, self).json_serialize()
        if info:
            res["info"] = info
        return res

    @classmethod
    def json_deserialize(cls, d) -> None | Theme:
        if "questions" not in d:
            return None
        t = Theme(d["name"])
        io = super().json_deserialize(d)
        if io:
            t.copy_info(io)
        t.questions.extend(d["questions"])
        return t

    def read_xml(self, el: Element) -> None:
        assert el.nodeName == "theme"

        el_info_l: List[Element] = el.getElementsByTagName("info")
        if el_info_l and el_info_l[0] in el.childNodes:
            super(Theme, self).read_xml(el_info_l[0])

        self.name = el.getAttribute("name")
        for el_question in el.getElementsByTagName("question"):
            question = Question()
            question.read_xml(el_question)
            # question = parse_question(el_question)
            self.questions.append(question)

    def write_xml(self, root: Document) -> Element:
        el: Element = root.createElement("theme")
        el.setAttribute("name", self.name)

        el_info = super(Theme, self).write_xml(root)
        if el_info:
            el.appendChild(el_info)

        if self.questions:
            el_questions = root.createElement("questions")
            el.appendChild(el_questions)
            for question in self.questions:
                el_question = question.write_xml(root)
                el_questions.appendChild(el_question)

        return el

    def __repr__(self) -> str:
        return f"SIGame Theme: {self.name}, questions {len(self.questions)}"


class QuestionTypes:
    SIMPLE = "simple"
    AUCTION = "auction"
    CAT = "cat"
    BAGCAT = "bagcat"
    SPONSORED = "sponsored"
    CHOICE = "choice"


class QuestionType(MutableMapping, Named, JSONSerializeable):
    def __init__(self, q_type: str) -> None:
        super().__init__(q_type)
        self.__params: List[QuestionTypeParam] = []

    def __getitem__(self, __key: str) -> str:
        for value in (p.value for p in self.__params if p.name == __key):
            return value
        return ""

    def __setitem__(self, __key: str, __value: str) -> None:
        for p in (p for p in self.__params if p.name == __key):
            p.value = __value
            return
        self.__params.append(QuestionTypeParam(__key, __value))

    def __delitem__(self, __key: str) -> None:
        __params: List[QuestionTypeParam] = [p for p in self.__params if p.value != __key]
        self.__params.clear()
        self.__params.extend(__params)

    def __iter__(self) -> Iterator[str]:
        return (p.name for p in self.__params)

    def __len__(self) -> int:
        return len(self.__params)

    def json_serialize(self):
        res = {
            "name": self.name
        }
        if len(self) != 0:
            res["param"] = {key.name: self[key.name] for key in self.__params}
        return res

    @classmethod
    def json_deserialize(cls, d) -> None | JSONSerializeable:
        return

    def __bool__(self):
        return True


class Question(InfoOwner, JSONSerializeable, XMLOp):
    def __init__(self, q_type: QuestionType = None, price: int = -1) -> None:
        super().__init__("")
        self.price: int = price
        self.q_type: QuestionType = q_type or QuestionType(QuestionTypes.SIMPLE)
        self.scenario: List[Atom] = []
        self.right: List[str] = []
        self.wrong: List[str] = []

    def json_serialize(self):
        res: Dict[str, Any] = {
            "price": self.price,
            "answers": {
                "right": self.right
            }
        }
        info = super(Question, self).json_serialize()
        if info:
            res["info"] = info
        if len(self.wrong) != 0:
            res["answers"]["wrong"] = self.wrong
        if self.q_type.name != QuestionTypes.SIMPLE:
            res["type"] = self.q_type
        res["scenario"] = self.scenario
        return res

    @classmethod
    def json_deserialize(cls, d: Dict[str, Any]) -> None | Question:
        if "scenario" not in d:
            return
        q_type: QuestionType | None = None
        if "type" in d:
            d_type: Dict[str, Any] = d["type"]
            q_type = QuestionType(d_type["name"])
            for p_name, p_value in d_type.get("param", {}).items():
                q_type[p_name] = p_value
        q = Question(q_type=q_type, price=d["price"])
        io = super().json_deserialize(d)
        if io:
            q.copy_info(io)
        q.scenario.extend(d["scenario"])
        # There should be at least one right answer
        q.right.extend(d["answers"]["right"])
        q.wrong.extend(d["answers"].get("wrong", []))
        return q

    def read_xml(self, el: Element) -> None:
        assert el.nodeName == "question"

        self.price = int(el.getAttribute("price") or self.price)

        el_info_l: List[Element] = el.getElementsByTagName("info")
        if el_info_l and el_info_l[0] in el.childNodes:
            super(Question, self).read_xml(el_info_l[0])

        el_type: List[Element] = el.getElementsByTagName("type")
        if len(el_type) != 0:
            type_name = el_type[0].getAttribute("name")
            param: List[Element] = el_type[0].getElementsByTagName("param")
            q_type = QuestionType(type_name)
            for el_param in param:
                name = el_param.getAttribute("name")
                value = el_param.childNodes[0].data if len(el_param.childNodes) != 0 else ""
                q_type[name] = value
            self.q_type = q_type

        el_scenario: Element = el.getElementsByTagName("scenario")[0]
        atoms = el_scenario.getElementsByTagName("atom")
        for el_atom in atoms:
            atom = Atom()
            atom.read_xml(el_atom)
            self.scenario.append(atom)

        el_right: List[Element] = el.getElementsByTagName("right")
        if len(el_right) != 0:
            answers = el_right[0].getElementsByTagName("answer")
            for el_answer in answers:
                self.right.append(helper.get_text(el_answer))

        el_wrong: List[Element] = el.getElementsByTagName("wrong")
        if len(el_wrong) != 0:
            answers = el_wrong[0].getElementsByTagName("answer")
            for el_answer in answers:
                self.wrong.append(helper.get_text(el_answer))

    def write_xml(self, root: Document) -> Element:
        el: Element = root.createElement("question")
        el.setAttribute("price", str(self.price))

        el_info = super(Question, self).write_xml(root)
        if el_info:
            el.appendChild(el_info)

        if self.q_type.name is not QuestionTypes.SIMPLE:
            el_type: Element = root.createElement("type")
            el_type.setAttribute("name", self.q_type.name)
            for name, value in self.q_type.items():
                el_param: Element = root.createElement("param")
                el_param.setAttribute("name", name)
                if value:
                    el_param.appendChild(root.createTextNode(value))
                el_type.appendChild(el_param)
            el.appendChild(el_type)

        el_scenario: Element = root.createElement("scenario")
        for atom in self.scenario:
            el_atom: Element = root.createElement("atom")
            if atom.time:
                el_atom.setAttribute("time", str(atom.time))
            if atom.type is not AtomTypes.TEXT:
                el_atom.setAttribute("type", atom.type)
            if atom.text:
                el_atom.appendChild(root.createTextNode(atom.text))
            el_scenario.appendChild(el_atom)
        el.appendChild(el_scenario)

        el_right: Element = root.createElement("right")
        for right in self.right:
            el_answer: Element = root.createElement("answer")
            if right:
                el_answer.appendChild(root.createTextNode(right))
            el_right.appendChild(el_answer)
        el.appendChild(el_right)

        if self.wrong:
            el_wrong: Element = root.createElement("wrong")
            for wrong in self.wrong:
                el_answer: Element = root.createElement("answer")
                if wrong:
                    el_answer.appendChild(root.createTextNode(wrong))
                el_wrong.appendChild(el_answer)
            el.appendChild(el_wrong)

        return el

    def __repr__(self) -> str:
        return f"SIGame Question, price: {self.price}"


class QuestionTypeParam(Named):
    def __init__(self, name: str, value: str = "") -> None:
        super().__init__(name)
        self.value: str = value


class AtomTypes:
    TEXT = "text"
    ORAL = "say"
    IMAGE = "image"
    AUDIO = "voice"
    VIDEO = "video"
    MARKER = "marker"


class Atom(JSONSerializeable, XMLOp):
    def __init__(self, text: str = "", a_type: str = AtomTypes.TEXT, time: int = 0) -> None:
        self.type: str = a_type
        self.text: str = text
        self.time: int = time

    def json_serialize(self):
        atom = {"text": self.text}
        if self.type != AtomTypes.TEXT:
            atom["type"] = self.type
        if self.time != 0:
            atom["time"] = self.time
        return atom

    @classmethod
    def json_deserialize(cls, d) -> None | Atom:
        if "text" not in d:
            return None
        text = d["text"]
        a_type = d.get("type", AtomTypes.TEXT)
        time = d.get("time", 0)
        atom = cls(text=text, a_type=a_type, time=time)
        return atom

    def read_xml(self, el: Element) -> None:
        assert el.nodeName == "atom"
        self.text = el.childNodes[0].data if len(el.childNodes) != 0 else ""
        time = el.getAttribute("time")
        self.time = 0 if time == "" else time
        a_type = el.getAttribute("type")
        self.type = AtomTypes.TEXT if a_type == "" else a_type

    def write_xml(self, root: Document) -> Element:
        pass

    def __repr__(self):
        return f"SIGame Atom, type \"{self.type}\", text \"{self.text}\""


class SIDocumentFormats:
    SIQ = "siq"
    JSIQ = "jsiq.zip"


class SIDocument:
    TEXT_STORAGE_NAME = "Texts"
    IMAGE_STORAGE_NAME = "Images"
    AUDIO_STORAGE_NAME = "Audio"
    VIDEO_STORAGE_NAME = "Video"

    def __init__(self, package: Package):
        self.package = package
        self.origin = None

    # This is very ugly. Too bad!
    def save_assets(self, other: ZipFile):
        with ZipFile(self.origin, "r") as ziporigin:
            for info in ziporigin.filelist:
                for foldername in (SIDocument.TEXT_STORAGE_NAME, SIDocument.IMAGE_STORAGE_NAME,
                                   SIDocument.AUDIO_STORAGE_NAME, SIDocument.VIDEO_STORAGE_NAME):
                    if info.filename.startswith(f"{foldername}/"):
                        filename = info.filename
                        with ziporigin.open(filename, "r") as from_file:
                            with other.open(filename, "w") as to_file:
                                shutil.copyfileobj(from_file, to_file)

    @classmethod
    def from_siq(cls, path) -> SIDocument:
        with ZipFile(path, "r") as zipfile:
            with zipfile.open("content.xml") as fp:
                document: Document = parse(fp)
        package = Package.from_document(document)
        doc = SIDocument(package)
        doc.origin = path
        return doc

    @classmethod
    def from_jsiq(cls, path):
        with ZipFile(path, "r") as zipfile:
            with zipfile.open("content.json") as fp:
                package: Package = json.load(fp, object_hook=json_object_hook)
        doc = SIDocument(package)
        doc.origin = path
        return doc

    def save_siq(self, path):
        with ZipFile(path, "w") as zipfile:
            with zipfile.open("content.xml", "w") as fp:
                root = Document()
                doc = self.package.write_xml(root)
                root.appendChild(doc)
                xml_str = root.toprettyxml(indent="    ")
                # xml_str = root.toprettyxml()
                fp.write(xml_str.encode("utf-8"))
                # json.dump(self.package, fp, default=default)
                # iterable = content_parser.SIJSONEncoder(ensure_ascii=False, indent=2).iterencode(self.package)
            self.save_assets(zipfile)

    def save_jsiq(self, path):
        with ZipFile(path, "w") as zipfile:
            with zipfile.open("content.json", "w") as fp:
                fp.write(json.dumps(self.package, default=json_default).encode("utf-8"))
                # json.dump(self.package, fp, default=default)
                # iterable = content_parser.SIJSONEncoder(ensure_ascii=False, indent=2).iterencode(self.package)
            self.save_assets(zipfile)


def json_default(o: Any) -> Any:
    if isinstance(o, JSONSerializeable):
        return o.json_serialize()
    return o
    # return JSONEncoder.default(self, o)


def json_object_hook(d: dict) -> JSONSerializeable | dict:
    data_cls: List[Type[JSONSerializeable]] = [Atom, Question, Theme, Round, Package]
    for cls in data_cls:
        res = cls.json_deserialize(d)
        if res:
            return res
    return d
