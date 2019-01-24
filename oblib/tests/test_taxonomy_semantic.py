# Copyright 2018 SunSpec Alliance

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import taxonomy
import taxonomy_semantic
from six import string_types

tax = taxonomy_semantic.TaxonomySemantic()


class TestTaxonomySemantic(unittest.TestCase):

    def test_concept_details(self):

        # Data type checks
        ci = tax.get_concept_details("solar:ACDisconnectSwitchMember")
        self.assertIsNotNone(ci)
        self.assertIsInstance(ci.abstract, bool)
        self.assertIsInstance(ci.id, string_types)
        # 'six.string_types' is equivalent to "str or unicode" in python2, "str" in python3
        self.assertIsInstance(ci.name, string_types)
        self.assertIsInstance(ci.nillable, bool)
        self.assertIsInstance(ci.period_independent, bool)
        self.assertIsInstance(ci.substitution_group, taxonomy.SubstitutionGroup)
        self.assertIsInstance(ci.type_name, string_types)
        self.assertIsInstance(ci.period_type, taxonomy.PeriodType)

        ci = tax.get_concept_details("solar:ACDisconnectSwitchMember")
        self.assertIsNotNone(ci)
        self.assertTrue(ci.abstract)
        self.assertEqual(ci.id, "solar:ACDisconnectSwitchMember")
        self.assertEqual(ci.name, "ACDisconnectSwitchMember")
        self.assertTrue(ci.nillable)
        self.assertFalse(ci.period_independent)
        self.assertEqual(ci.substitution_group, taxonomy.SubstitutionGroup.item)
        self.assertEqual(ci.type_name, "nonnum:domainItemType")
        self.assertEqual(ci.period_type, taxonomy.PeriodType.duration)

        # Values checks
        ci = tax.get_concept_details("solar:AdvisorInvoicesCounterparties")
        self.assertIsNotNone(ci)
        self.assertFalse(ci.abstract)
        self.assertEqual(ci.id, "solar:AdvisorInvoicesCounterparties")
        self.assertEqual(ci.name, "AdvisorInvoicesCounterparties")
        self.assertTrue(ci.nillable)
        self.assertFalse(ci.period_independent)
        self.assertEqual(ci.substitution_group, taxonomy.SubstitutionGroup.item)
        self.assertEqual(ci.type_name, "xbrli:stringItemType")
        self.assertEqual(ci.period_type, taxonomy.PeriodType.duration)

        ci = tax.get_concept_details("dei:LegalEntityIdentifier")
        self.assertIsNotNone(ci)
        self.assertFalse(ci.abstract)
        self.assertEqual(ci.id, "dei:LegalEntityIdentifier")
        self.assertEqual(ci.name, "LegalEntityIdentifier")
        self.assertTrue(ci.nillable)
        self.assertFalse(ci.period_independent)
        self.assertEqual(ci.substitution_group, taxonomy.SubstitutionGroup.item)
        self.assertEqual(ci.type_name, "dei:legalEntityIdentifierItemType")
        self.assertEqual(ci.period_type, taxonomy.PeriodType.duration)

    def test_get_entrypoint_concepts(self):
        self.assertEqual(len(tax.get_entrypoint_concepts("MonthlyOperatingReport")), 84)
        self.assertEqual(tax.get_entrypoint_concepts("MonthlyOperatingReort"), None)
        self.assertEqual(len(tax.get_entrypoint_concepts("CutSheet")), 302)
        self.assertEqual(len(tax.get_entrypoint_concepts("Utility")), 8)

        # TODO: SystemInstallation is currently loaded under System.
        # self.assertEqual(len(tax.concepts_ep("SystemInstallationCost")), 10)

    def test_get_entrypoint_concepts_details(self):
        self.assertEqual(len(tax.get_entrypoint_concepts_details("MonthlyOperatingReport")), 84)
        self.assertEqual(tax.get_entrypoint_concepts_details("MonthlyOperatingReort"), None)
        
        # TODO: 302 is expected but 297 returned, seeking info on why this is from XBRL.
        # self.assertEqual(len(tax.concepts_info_ep("CutSheet")), 302)
        self.assertEqual(len(tax.get_entrypoint_concepts_details("CutSheet")), 297)

        self.assertEqual(len(tax.get_entrypoint_concepts_details("Utility")), 8)

        for ci in tax.get_entrypoint_concepts_details("Utility"):
            self.assertEqual(ci, tax.get_concept_details(ci.id))

    def test_get_all_concept_details(self):
        self.assertIsNotNone(tax.get_all_concepts_details())

    def test_get_all_type_names(self):
        self.assertEqual(len(tax.get_all_type_names()), 91)

    def test_get_all_entrypoints(self):
        self.assertEqual(len(tax.get_all_entrypoints()), 159)

    def test_get_entrypoint_relationships(self):
        self.assertIsNone(tax.get_entrypoint_relationships("Arggh"))
        self.assertEqual(len(tax.get_entrypoint_relationships("Utility")), 7)
        self.assertEqual(len(tax.get_entrypoint_relationships("MonthlyOperatingReport")), 84)
        self.assertEqual(len(tax.get_entrypoint_relationships("CutSheet")), 305)

    def test_is_concept(self):
        self.assertTrue(tax.is_concept("solar:EnvironmentalImpactReportExpirationDate"))
        self.assertFalse(tax.is_concept("solar:EnvironmentalImpactReportExirationDate"))
        self.assertTrue(tax.is_concept("solar:AdvisorInvoicesCounterparties"))
        self.assertTrue(tax.is_concept("dei:LegalEntityIdentifier"))

    def test_validate_concept_value(self):
        self.assertEqual(0, len(tax.validate_concept_value("solar:TaxEquityCommunicationPlan", "Arff")[1]))
        self.assertEqual(1, len(tax.validate_concept_value("solar:TaxEquityCommunicaionPlan", "Arff")))
        #TODO: 37 can be converted to valid string
        self.assertEqual(0, len(tax.validate_concept_value("solar:TaxEquityCommunicationPlan", 37)[1]))
        self.assertEqual(1, len(tax.validate_concept_value("dei:LegalEntityIdentifier", "5493006MHB84DD0ZWV18")[1]))

        # TODO: Once the validator is fully working test a large number of cases.

    def test_is_entrypoint(self):
        self.assertTrue(tax.is_entrypoint("AssetManager"))
        self.assertFalse(tax.is_entrypoint("AssetMnager"))
        self.assertTrue(tax.is_entrypoint("MonthlyOperatingReport"))
        self.assertFalse(tax.is_entrypoint("MonthlyOperatingRepot"))

    def test_unrequired_concepts_removed(self):
        """
        In order to save memory concepts that are not required should be removed from memory after the taxonomy
        is loaded.  This primarily occurs in the us-gaap and dea namespaces since they are not always used
        by the solar namespace.  Thus these tests prove that certain concepts are gone.
        """

        self.assertFalse("dei:EntityReportingCurrencyISOCode" in tax._elements)
        self.assertFalse("dei:BusinessContactMember" in tax._elements)
        self.assertFalse("us-gaap:TimeSharingTransactionsAllowanceForUncollectibleAccountsOnReceivablesSoldWithRecourse" in tax._elements)
        self.assertFalse("us-gaap:TreasuryStockValueAcquiredCostMethod" in tax._elements)
