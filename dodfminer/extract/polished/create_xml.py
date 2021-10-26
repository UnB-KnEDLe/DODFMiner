import os
import datetime
import re
from lxml import etree
from dodfminer.extract.pure.core import ContentExtractor as ce

class XMLFy:
    '''Cria um xml com informações de um ato'''

    def __init__(self, file, acts_ids, id_xml):
        self._file = file
        self._acts_ids = acts_ids
        self._xml_id = self.build_xml_id(id_xml)
        self._annotation_id = 1
        self._relations_id = 1
        self.xml = self._create_xml()

    def build_xml_id(self, id_xml):
        file_name = self._file.split('/')[-1]

        str2int2str = lambda x : str(int(x))
        file_numbers_list = map(str2int2str, re.findall(r'\d+', file_name))

        file_id = ".".join(list(file_numbers_list)[1:])

        return f"{id_xml}_{file_id}"

    def print_tree(self):
        print(etree.tostring(self.xml, pretty_print=True).decode())

    def save_to_disc(self, path):
        doc_type = """<!DOCTYPE collection SYSTEM "BioC.dtd">"""
        if os.path.isfile(path):
            folder_path = os.path.splitext(path)[0]
            print(folder_path)
        else:
            folder_path = path
        self.xml.write(os.path.join(folder_path, self._xml_id+".xml"), pretty_print=True, xml_declaration=True,
                      encoding="utf-8", doctype=doc_type)


    def _create_xml(self):
        doc = self._creat_collection()
        tree = etree.ElementTree(doc)
        return tree


    def _creat_collection(self):
        root_collect = etree.Element('collection')
        root_collect.append(etree.Element('source'))
        root_collect.append(etree.Element('date'))
        root_collect.append(etree.Element('key'))

        doc = self._create_document()

        root_collect.append(doc)

        return root_collect


    def _create_document(self):
        root_doc = etree.Element('document')

        child_id = etree.Element('id')
        child_id.text = str(self._xml_id)
        root_doc.append(child_id)

        infon = etree.Element('infon')
        infon.set("key", "tt_curatable")
        infon.text = "no"
        root_doc.append(infon)

        infon = etree.Element('infon')
        infon.set("key", "tt_version")
        infon.text = "0"
        root_doc.append(infon)

        infon = etree.Element('infon')
        infon.set("key", "tt_round")
        infon.text = "0"
        root_doc.append(infon)

        self._text_to_passages(root_doc)

        return root_doc

    def _text_to_passages(self, root):
        text = ce.extract_text(self._file, single=False,
                                  block=True, sep=' ', norm='NFKD')
        offset = 0
        for line in text:
            _, _, _, _, text = line
            annotation = self.execute_regex(text)
            child = self._create_passage(offset, text, annotation)
            root.append(child)
            offset += len(text)-1

    # pylint: disable=protected-access
    def execute_regex(self, text):
        res = {}
        for key in self._acts_ids:
            act = self._acts_ids[key](text, "regex")
            if act._acts:
                res[key] = act._acts
        return res

    def _create_passage(self, offset, text, an_dict):
        root_passage = etree.Element('passage')

        child_offset = etree.Element('offset')
        child_offset.text = str(offset)
        root_passage.append(child_offset)

        child_text = etree.Element('text')
        child_text.text = text
        root_passage.append(child_text)

        # relations = []
        # if an_dict:
        for act_type in an_dict:
            for act_inst in an_dict[act_type]:
                # relations_ids = []
                for prop_type, value in act_inst.items():
                    if isinstance(value, str):
                        offset_sum = text.find(value)
                        text = text.replace(value, '_'*len(value), 1)
                        if offset_sum != -1:
                            offset_prop = offset + offset_sum
                            child_annotation = self._annotate(prop_type,
                                                                value, offset_prop)
                            root_passage.append(child_annotation)
                            # relations_ids.append(self._annotation_id)
                            self._annotation_id += 1
                # child_rel = self._create_relation("Ato_"+act_type.capitalize(), relations_ids)
                # relations.append(child_rel)
                # self._relations_id += 1

        # for relation in relations:
        #     root_passage.append(relation)

        return root_passage

    def _annotate(self, annotation_type, text, offset):
        root_annotate = etree.Element('annotation')
        root_annotate.set("id", str(self._annotation_id))

        infon = etree.Element('infon')
        infon.set("key", "type")
        infon.text = annotation_type
        root_annotate.append(infon)

        infon = etree.Element('infon')
        infon.set("key", "identifier")
        root_annotate.append(infon)

        infon = etree.Element('infon')
        infon.set("key", "annotator")
        infon.text = "DODFMiner"
        root_annotate.append(infon)

        infon = etree.Element('infon')
        infon.set("key", "updated_at")
        infon.text = str(datetime.datetime.now())
        root_annotate.append(infon)

        location = etree.Element('location')
        location.set("offset", str(offset))
        location.set("length", str(len(text)))
        root_annotate.append(location)

        annotation_txt = etree.Element('text')
        annotation_txt.text = text
        root_annotate.append(annotation_txt)

        return root_annotate

    def _create_relation(self, relation_type, annotations):
        root_relation = etree.Element('relation')
        root_relation.set("id", "R"+str(self._relations_id))

        infon = etree.Element('infon')
        infon.set("key", "type")
        infon.text = relation_type
        root_relation.append(infon)

        infon = etree.Element('infon')
        infon.set("key", "annotator")
        infon.text = "DODFMiner"
        root_relation.append(infon)

        infon = etree.Element('infon')
        infon.set("key", "updated_at")
        infon.text = str(datetime.datetime.now())
        root_relation.append(infon)

        for ann_id in annotations:
            node = etree.Element('node')
            node.set("refid", str(ann_id))
            node.set("role", "")
            root_relation.append(node)

        return root_relation
