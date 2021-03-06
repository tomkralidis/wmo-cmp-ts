# -*- coding: utf-8 -*-
# =================================================================
#
# Terms and Conditions of Use
#
# Unless otherwise noted, computer program source code of this
# distribution # is covered under Crown Copyright, Government of
# Canada, and is distributed under the MIT License.
#
# The Canada wordmark and related graphics associated with this
# distribution are protected under trademark law and copyright law.
# No permission is granted to use them outside the parameters of
# the Government of Canada's corporate identity program. For
# more information, see
# http://www.tbs-sct.gc.ca/fip-pcim/index-eng.asp
#
# Copyright title to all 3rd party software distributed with this
# software is held by the respective copyright holders as noted in
# those files. Users are asked to read the 3rd Party Licenses
# referenced with those assets.
#
# Copyright (c) 2016 Government of Canada
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import logging
from wmo_cmp_ts.util import get_codelists, NAMESPACES, nspath_eval, \
    validate_iso_xml

LOGGER = logging.getLogger(__name__)

CODELIST_PREFIX = 'http://wis.wmo.int/2012/codelists/WMOCodeLists.xml'


def msg(testid, test_description):
    """Convenience function to print test props"""
    requirement = testid.split('test_requirement_')[-1].replace('_', '.')
    return 'Requirement %s:\n    %s' % (requirement, test_description)


def gen_test_id(tid):
    """Convenience function to print Test id"""
    return 'http://wis.wmo.int/2012/metadata/conf/%s' % tid


class WMOCoreMetadataProfileTestSuite13(object):
    """Test suite for WMO Core Metadata Profile assertions"""

    def __init__(self, exml):
        """init"""
        self.test_id = None
        self.exml = exml  # serialized already
        self.namespaces = self.exml.getroot().nsmap

        # generate dict of codelists
        self.codelists = get_codelists()

    def run_tests(self):
        """Wrapper function to run all tests"""
        tests = ['6_1_1', '6_1_2', '6_2_1', '6_3_1', '8_1_1',
                 '8_2_1', '8_2_2', '8_2_3', '8_2_4', '9_1_1',
                 '9_2_1', '9_3_1', '9_3_2']

        error_stack = []
        for i in tests:
            test_name = 'test_requirement_%s' % i
            try:
                getattr(self, test_name)()
            except AssertionError as err:
                message = 'ASSERTION ERROR: %s' % err
                LOGGER.error(message)
                error_stack.append(message)
            except Exception as err:
                message = 'OTHER ERROR: %s' % err
                LOGGER.error(message)
                error_stack.append(message)

        if len(error_stack) > 0:
            raise TestSuiteError('Invalid metadata', error_stack)

    def test_requirement_6_1_1(self):
        """Requirement 6.1.1: Each WIS Discovery Metadata record shall validate without error against the XML schemas defined in ISO/TS 19139:2007."""
        self.test_id = gen_test_id('ISO-TS-19139-2007-xml-schema-validation')
        validate_iso_xml(self.exml)

    def test_requirement_6_1_2(self):
        """Requirement 6.1.2: Each WIS Discovery Metadata record shall validate without error against the rule-based constraints listed in ISO/TS 19139:2007 Annex A (Table A.1)."""
        self.test_id = gen_test_id('ISO-TS-19139-2007-rule-based-validation')
        # TODO

    def test_requirement_6_2_1(self):
        """Requirement 6.2.1: Each WIS Discovery Metadata record shall explicitly name all namespaces used within the record; use of default namespaces is prohibited."""
        self.test_id = gen_test_id('explicit-xml-namespace-identification')

        assert(None not in self.namespaces), self.test_requirement_6_2_1.__doc__

    def test_requirement_6_3_1(self):
        """Requirement 6.3.1: Each WIS Discovery Metadata record shall declare the following XML namespace for GML: http://www.opengis.net/gml/3.2."""
        self.test_id = gen_test_id('gml-namespace-specification')

        if 'gml' in self.namespaces:
            assert(self.namespaces['gml'] == NAMESPACES['gml']), self.test_requirement_6_3_1.__doc__

    def test_requirement_8_1_1(self):
        """Requirement 8.1.1: Each WIS Discovery Metadata record shall include one gmd:MD_Metadata/gmd:fileIdentifier attribute."""
        self.test_id = gen_test_id('fileIdentifier-cardinality')

        ids = self.exml.findall(nspath_eval('gmd:fileIdentifier'))
        assert(len(ids) == 1), self.test_requirement_8_1_1.__doc__

    def test_requirement_8_2_1(self):
        """Requirement 8.2.1: Each WIS Discovery Metadata record shall include at least one keyword from the WMO_CategoryCode code list."""
        self.test_id = gen_test_id('WMO_CategoryCode-keyword-cardinality')

        found = 0

        # (i) check thesaurus
        wmo_cats = self._get_wmo_keyword_lists()
        assert(len(wmo_cats) > 0), self.test_requirement_8_2_1.__doc__

        # (ii) check all WMO keyword sets valid codelist value
        for cat in wmo_cats:
            for keyword in cat.findall(nspath_eval('gmd:keyword/gco:CharacterString')):
                if keyword.text in self.codelists['WMO_CategoryCode']:
                    found = 1
                    break

        assert(found == 1), self.test_requirement_8_2_1.__doc__

    def test_requirement_8_2_2(self):
        """Requirement 8.2.2: Keywords from WMO_CategoryCode code list shall be defined as keyword type "theme"."""
        self.test_id = gen_test_id('WMO_CategoryCode-keyword-theme')

        wmo_cats = self._get_wmo_keyword_lists()
        assert(len(wmo_cats) > 0), self.test_requirement_8_2_2.__doc__

        for cat in wmo_cats:
            for keyword_type in cat.findall(nspath_eval('gmd:type/gmd:MD_KeywordTypeCode')):
                assert(keyword_type.text == 'theme'), self.test_requirement_8_2_2.__doc__

    def test_requirement_8_2_3(self):
        """Requirement 8.2.3: All keywords sourced from a particular keyword thesaurus shall be grouped into a single instance of the MD_Keywords class."""
        self.test_id = gen_test_id('keyword-grouping')

        unique = 0
        thesauri = []
        wmo_cats = self._get_wmo_keyword_lists()
        assert(len(wmo_cats) > 0), self.test_requirement_8_2_3.__doc__

        for cat in wmo_cats:
            for node in cat.findall(nspath_eval('gmd:thesaurusName/gmd:CI_Citation/gmd:title')):
                if node is not None:
                    node2 = node.find(nspath_eval('gmx:Anchor'))
                    if node2 is not None:  # search gmx:Anchor
                        value = node2.text
                    else:  # gmd:title should be WMO_CategoryCode
                        value = node.text
                    thesauri.append(value)

        if len(thesauri) == 1:
            unique = 1
        else:  # check if list if unique
            thesauri2 = list(set(thesauri))
            if len(thesauri) == len(thesauri2):
                unique = 1

        assert(unique == 1), self.test_requirement_8_2_3.__doc__

    def test_requirement_8_2_4(self):
        """Requirement 8.2.4: Each WIS Discovery Metadata record describing geographic data shall include the description of at least one geographic bounding box defining the spatial extent of the data"""
        self.test_id = gen_test_id('geographic-bounding-box')

        hierarchy = self.exml.find(nspath_eval('gmd:hierarchyLevel/gmd:MD_ScopeCode'))
        assert(hierarchy.text != 'nonGeographicDataset'), self.test_requirement_8_2_4.__doc__

        bbox = self.exml.find(nspath_eval('gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox'))
        assert(bbox is not None), self.test_requirement_8_2_4.__doc__

    def test_requirement_9_1_1(self):
        """Requirement 9.1.1: A WIS Discovery Metadata record describing data for global exchange via the WIS shall indicate the scope of distribution using the keyword "GlobalExchange" of type "dataCenterdataCentre" from thesaurus WMO_DistributionScopeCode."""
        self.test_id = gen_test_id('identification-of-globally-exchanged-data')

        dist_cats = self._get_wmo_keyword_lists('WMO_DistributionScopeCode')
        if len(dist_cats) > 0:
            for cat in dist_cats:
                for keyword_type in cat.findall(nspath_eval('gmd:type/gmd:MD_KeywordTypeCode')):
                    assert(keyword_type.text == 'dataCentre'), self.test_requirement_9_1_1.__doc__

            assert('GlobalExchange' in dist_cats), self.test_requirement_9_1_1.__doc__

    def test_requirement_9_2_1(self):
        """Requirement 9.2.1: A WIS Discovery Metadata record describing data for global exchange via the WIS shall have a gmd:MD_Metadata/gmd:fileIdentifier attribute formatted as follows (where {uid} is a unique identifier derived from the GTS bulletin or file name): urn:x-wmo:md:int.wmo.wis::{uid}."""
        self.test_id = gen_test_id('fileIdentifier-for-globally-exchanged-data')

        mask = 'urn:x-wmo:md:int.wmo.wis::'
        identifier = self.exml.find(nspath_eval('gmd:fileIdentifier/gco:CharacterString')).text

        assert(identifier.startswith(mask)), self.test_requirement_9_2_1.__doc__

    def test_requirement_9_3_1(self):
        """Requirement 9.3.1: A WIS Discovery Metadata record describing data for global exchange via the WIS shall indicate the WMO Data License as Legal Constraint (type: "otherConstraints") using one and only one term from the WMO_DataLicenseCode code list."""
        self.test_id = gen_test_id('WMO-data-policy-for-globally-exchanged-data')

        count = 0
        other_constraints = [legal.text for legal in self.exml.findall(nspath_eval('gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString'))]
        for constr in other_constraints:
            if constr in self.codelists['WMO_DataLicenseCode']:
                count += 1
        assert(count == 1), self.test_requirement_9_3_1.__doc__

    def test_requirement_9_3_2(self):
        """Requirement 9.3.2: A WIS Discovery Metadata record describing data for global exchange via the WIS shall indicate the GTS Priority as Legal Constraint (type: "otherConstraints") using one and only one term from the WMO_GTSProductCategoryCode code list."""
        self.test_id = gen_test_id('GTS-priority-for-globally-exchanged-data')

        count = 0
        other_constraints = [legal.text for legal in self.exml.findall(nspath_eval('gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString'))]
        for constr in other_constraints:
            if constr in self.codelists['WMO_GTSProductCategoryCode']:
                count += 1
        assert(count == 1), self.test_requirement_9_3_2.__doc__

    def _get_wmo_keyword_lists(self, code='WMO_CategoryCode'):
        """Helper function to retrive all keyword sets by code"""
        wmo_cats = []

        keywords_sets = self.exml.findall(nspath_eval('gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords'))

        for kwd in keywords_sets:  # find thesaurusname
            node = kwd.find(nspath_eval('gmd:thesaurusName/gmd:CI_Citation/gmd:title'))
            if node is not None:
                node2 = node.find(nspath_eval('gmx:Anchor'))
                if node2 is not None:  # search gmx:Anchor
                    value = node2.get(nspath_eval('xlink:href'))
                    if value == '%s#%s' % (CODELIST_PREFIX, code):
                        wmo_cats.append(kwd)
                else:  # gmd:title should be code var
                    value = node.find(nspath_eval('gco:CharacterString')).text
                    if value == code:
                        wmo_cats.append(kwd)
        return wmo_cats


class TestSuiteError(Exception):
    """custom exception handler"""
    def __init__(self, message, errors):
        """set error list/stack"""
        super(TestSuiteError, self).__init__(message)
        self.errors = errors
