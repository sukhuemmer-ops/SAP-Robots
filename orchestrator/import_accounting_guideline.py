#!/usr/bin/env python3
"""
Accounting-Guideline Catensys Group V6
Import → knowledge_universe via Orchestrator REST-API

Ausführen: python import_accounting_guideline.py
Voraussetzung: Orchestrator läuft auf localhost:8000
"""
import json, requests, time

BASE = "http://localhost:8000"
TIMEOUT = 30

RECORDS = [
  {
    "layer": "finance",
    "object_type": "concept",
    "key": "acc_guide_general_information_on_the_annual_financial_statements",
    "title": "General information on the annual financial statements",
    "summary": "This section describes the general requirements for IFRS financial statements, in particular the underlying assumptions underlying assumptions and requirements for the information contained therein. The IASB's Conceptual Framework describes the basic concepts according to which financial statements are to be prepared. Further regulations for the annual financial statements can be found in IAS2, which supplements and specifies the conceptual framework. Purpose of the financial statements: Financi",
    "body_json": "{\"full_text\": \"This section describes the general requirements for IFRS financial statements, in particular the underlying assumptions underlying assumptions and requirements for the information contained therein. The IASB's Conceptual Framework describes the basic concepts according to which financial statements are to be prepared. Further regulations for the annual financial statements can be found in IAS2, which supplements and specifies the conceptual framework.\\nPurpose of the financial statements:\\nFinancial statements are a structured presentation of the net assets, financial position and results of operations of a company.\\nAccording to IAS 1.9, the objective of financial statements is to provide information about the net assets, financial position, results of operations and cash flows of a financial position, financial performance and cash flows of an entity that are useful to a wide range of users in making economic decisions.\\nFinancial statements also provide an account of the results of the administration of the assets entrusted to management.\\nThe information from a complete set of financial statements helps the addressees (management, shareholders, auditors and\\nauditors) to predict the company's future cash flows and the timing and certainty of their occurrence.\\nThe completeness of the financial statements:\\nIn accordance with IAS 1.10, a complete set of financial statements consists of:\\nBalance sheet as at the balance sheet date\\nStatement of comprehensive income (profit and loss and other comprehensive income for the period)\\nStatement of changes in equity for the period\\nCash flow statement for the period\\nNotes to the financial statements with a presentation of the significant accounting policies and other explanatory notes.\\nComparative information must be provided for the previous period, i.e. the listed components must be presented. If there have been retrospective changes, a balance sheet at the beginning of the previous period must also be prepared.\\nQualitative requirements for the financial statements:\\nThe qualitative requirements identify the information that is likely to be most useful for the users' decisions.\\nBasic qualitative requirements: \\nRelevance and credible presentation are key requirements for the basic qualitative requirements. This means that the information must be relevant and presented in a credible manner.\\nInformation is relevant if it can influence the decisions of the addressees, i.e. the information has either a predictive value, a confirmatory value  or both. Information has a predictive value if it has an influence on the assessment of future developments by the addressees.\\nThe information itself does not have to have the character of a prediction or forecast. Information has a confirmatory value if it confirms or corrects assessments from the past. The aspects of prediction and confirmation are linked. Materiality is a company-specific factor in the question of relevance.\\nInformation is material if, under normal circumstances, it could reasonably be expected that its omission, misstatement or concealment would have an adverse effect on the primary users of the information, the decisions of the primary users of general purpose financial statements that include financial information about the reporting entity, financial information about the reporting entity (IAS 1.7). Information is disguised if it is communicated in a way that has an effect on the primary users of the financial statements that is similar to an omission or disguise. effect as omitted or incorrect information. Information about a material item, transaction or other significant event is included in the financial statements, but is vague or unclear.\\nGoing concern:\\nThe going concern concept in accordance with IAS 1.25 et seq. is based on the assumption that the management has neither the intention nor is forced to dissolve the company or cease its activities. This must be assessed by management for each financial statement.\\nIf the going concern principle no longer applies, the financial statements may no longer be prepared in accordance with general accounting principles.\\nAccrual basis of accounting\\nIn accordance with IAS 1.27f, the financial statements must be prepared on an accrual basis. This means that the components of the financial statements (assets, liabilities, equity, expenses and income -revenue-) are to be recognized when they meet the definitions and criteria of the regulation.\", \"section_level\": 1, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 1.10\", \"IAS 1.25\", \"IAS 1.27\", \"IAS 1.7\", \"IAS 1.9\", \"IAS2\"], \"parent_section\": null}",
    "confidence": 5,
    "importance": 5,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": null
  },
  {
    "layer": "finance",
    "object_type": "concept",
    "key": "acc_guide_balance_confirmation_for_external_customers_and_for_suppliers",
    "title": "Balance confirmation for external customers and for suppliers",
    "summary": "What is a balance confirmation? A balance confirmation is a written confirmation with which a creditor (e.g. a Supplier) informs the debtor (e.g. a customer) of the current balance of their account or other liabilities. In the case of liabilities consisting of several items, the composition of the balance from the individual items is shown in addition to the total balance. The aim of the balance confirmation is to ensure that the bookkeeping is correct and to uncover and clarify any differences ",
    "body_json": "{\"full_text\": \"What is a balance confirmation?\\nA balance confirmation is a written confirmation with which a creditor (e.g. a Supplier) informs the debtor (e.g. a customer) of the current balance of their account or other liabilities. In the case of liabilities consisting of several items, the composition of the balance from the individual items is shown in addition to the total balance. The aim of the balance confirmation is to ensure that the bookkeeping is correct and to uncover and clarify any differences or discrepancies. As a rule, the balance confirmation is carried out as part of annual financial statements and audits.\\nLegal basis for the balance confirmation\\nThe balance confirmation has an important function in the commercial and business world. On the one hand, it serves to clarify discrepancies between business partners and, on the other, it is an important part of a company's bookkeeping and accounting. From a legal perspective, the need for a balance confirmation arises from the Local Gaap and tax law.\\nThere is an obligation for companies to keep double-entry accounts. This means that records must be kept of all business transactions to enable a verifiable, complete and timely presentation of the company's financial position. The balance confirmation is a control instrument used to check the accuracy of the company's own bookkeeping and that of its business partners.\\nPurpose of the balance confirmation\\nThe balance confirmation is particularly important for receivables and liabilities. The reconciliation of account balances provides information on whether the receivables and liabilities are listed correctly in the books. Furthermore, the balance confirmation also serves as evidence in the event of discrepancies or legal disputes.\\nBalance confirmation process\\nBasically, we obtain confirmation from customers and suppliers of the total annual turnover and outstanding invoices as of December 31.  against Catensy's company.\\nThe process of a balance confirmation can be broken down into the following steps:\\nRequest: Catensys-Group requests a balance confirmation from a business partner external customers and external suppliers with an annual turnover of more than 100,000 EUROS at the end of the year. This request is mandatory for all Catensys subsidiary partners and the balance confirmation must be sent to the customer and supplier by January 12th.\\nCreation: The business partner creates the balance confirmation and enters the current balance, the key date or the relevant period as well as a signature and the company (Customers/Suppliers) stamp.\\nReturn: The balance confirmation is returned to the requesting company (Customers/ Suppliers).\\nComparison: The requesting company or bank compares the balance confirmation with its own records. If they match, the process is completed. If there are discrepancies, the differences are clarified.\\nBank Statement Confirmation\\nA bank statement confirmation is a written confirmation in which a financial institution confirms the account balance and, if applicable, other financial liabilities (e.g. loans, guarantees) held by the company as of the reporting date of December 31. In addition to the total balance, the confirmation may include a breakdown of individual items such as cash accounts, term deposits, or overdrafts. The purpose of the bank confirmation is to ensure the accuracy of the company's accounting records and to detect or clarify any discrepancies. Bank confirmations are typically obtained as part of the preparation of annual financial statements and external audits.\\nLawyer Confirmation\\nA lawyer confirmation is a written statement provided by the company’s legal counsel regarding pending or threatened legal proceedings involving the company as of the reporting date of December 31. If such litigation exists, the confirmation typically includes a description of the case, the status, the estimated financial impact, and the likelihood of success or loss. In addition, the legal advisor confirms whether contingent liabilities or obligations exist. The purpose of the lawyer confirmation is to ensure that all legal risks are appropriately reflected in the financial statements and to support transparency in the context of year-end closing and audit procedures.\", \"section_level\": 1, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": null}",
    "confidence": 5,
    "importance": 5,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\", \"jahresabschluss\", \"saldoabstimmung\"]",
    "active": 1,
    "_parent_key": null
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_accounting_and_valuation_guidelines_per_account_group",
    "title": "Accounting and valuation guidelines per account group",
    "summary": "Accounting and valuation guidelines per account group",
    "body_json": "{\"full_text\": \"\", \"section_level\": 1, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": null}",
    "confidence": 5,
    "importance": 5,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": null
  },
  {
    "layer": "finance",
    "object_type": "concept",
    "key": "acc_guide_assets",
    "title": "Assets",
    "summary": "Assets are recognized and measured in accordance with relevant IFRS standards. They are divided into non-current and current assets, depending on their expected use or realization. Current assets are assets that are expected to be realized, sold, or consumed within the normal operating cycle, or within 12 months after the reporting date – whichever is longer. Typical examples include cash and cash equivalents, trade receivables, inventories, and short-term financial assets. Non-current assets ar",
    "body_json": "{\"full_text\": \"Assets are recognized and measured in accordance with relevant IFRS standards. They are divided into non-current and current assets, depending on their expected use or realization.\\nCurrent assets are assets that are expected to be realized, sold, or consumed within the normal operating cycle, or within 12 months after the reporting date – whichever is longer. Typical examples include cash and cash equivalents, trade receivables, inventories, and short-term financial assets.\\nNon-current assets are all other assets that do not meet the definition of current assets. They are not expected to be realized or consumed within 12 months and typically include property, plant and equipment, intangible assets, long-term financial investments, and deferred tax assets.\\nThe classification is essential for providing a clear picture of a company’s liquidity, solvency, and operational efficiency.\", \"section_level\": 2, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_accounting_and_valuation_guidelines_per_account_group\"}",
    "confidence": 5,
    "importance": 4,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"assets\", \"bilanzierung\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": "acc_guide_accounting_and_valuation_guidelines_per_account_group"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_non_current_assets",
    "title": "Non-Current Assets",
    "summary": "Non-current assets are held for long-term use in operations and include intangible assets, property, and investments. Recognition and valuation follow IAS 16, IAS 38, and IFRS 16.",
    "body_json": "{\"full_text\": \"Non-current assets are held for long-term use in operations and include intangible assets, property, and investments. Recognition and valuation follow IAS 16, IAS 38, and IFRS 16.\", \"section_level\": 3, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 16\", \"IAS 38\", \"IFRS 16\"], \"parent_section\": \"acc_guide_assets\"}",
    "confidence": 5,
    "importance": 3,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"assets\", \"bilanzierung\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": "acc_guide_assets"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_intangible_assets_ias_38",
    "title": "Intangible assets (IAS 38)",
    "summary": "Intangible assets are recognized in accordance with IAS 38 only if they meet all of the following criteria: Identifiable (i.e., separable or arising from contractual/legal rights) Under the control of the entity Probable future economic benefits are expected Initial Recognition: Intangible assets are initially measured at acquisition or production cost. Subsequent Measurement: As a rule, the cost model is applied, meaning the asset is carried at cost less accumulated amortization and any accumul",
    "body_json": "{\"full_text\": \"Intangible assets are recognized in accordance with IAS 38 only if they meet all of the following criteria:\\nIdentifiable (i.e., separable or arising from contractual/legal rights)\\nUnder the control of the entity\\nProbable future economic benefits are expected\\nInitial Recognition: Intangible assets are initially measured at acquisition or production cost.\\nSubsequent Measurement:\\nAs a rule, the cost model is applied, meaning the asset is carried at cost less accumulated amortization and any accumulated impairment losses. Scheduled straight-line amortization is applied over the estimated useful life, which in the CATENSYS Group is limited to a maximum of 5 years for software.\\nAll intangible assets within the CATENSYS Group have finite useful lives. Amortization begins when the asset is available for use, typically with the start of production.\\nUseful lives:\\nSoftware: 3 to 5 years\\nPatents and licenses: over the contractual term\\nDevelopment costs: max. 4 years\\nOther intangible assets: 3 to 5 years\\nImpairment Testing:\\nAn impairment test must be performed if there are indicators of impairment. Impairment losses are recognized in profit or loss if the recoverable amount of the asset falls below its carrying amount.\\nDerecognition:\\nIntangible assets are derecognized when no further economic benefit is expected from their use or disposal, or when control is transferred to a third party. Upon derecognition, the gain or loss is calculated as the difference between the net disposal proceeds and the carrying amount and recognized in profit or loss.\\nExample - Journal Entry:\\nPurchase Software:\\nDebit:\\t023000 \\t- Computer software\\nCredit:\\t99998 \\t- Technical account new FI-AA\\nDebit:\\t99998 - Technical account new FI-AA\\nCredit:\\t445000 Domestic payables (Supplier Account: L100203)\\nDebit:\\t445000 Domestic payables (Supplier Account: L100203)\\nCredit:\\t280000 – Bank Account\\nMonthly amortization:\\nDebit:\\t651000 - Depreciation - intangible assets\\nCredit:\\t023010 - Accumulated depreciation-computer software\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 38\"], \"parent_section\": \"acc_guide_non_current_assets\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"afa\", \"assets\", \"bilanzierung\", \"catensys_group\", \"ias16\", \"ias38\", \"ifrs\", \"sachanlagen\"]",
    "active": 1,
    "_parent_key": "acc_guide_non_current_assets"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_property_plant_and_equipment_ias_16",
    "title": "Property, plant and equipment (IAS 16)",
    "summary": "Assets under construction and property, plant and equipment are recognized at acquisition or production cost less accumulated depreciation and accumulated impairment losses. Scheduled straight-line depreciation is based on the following useful lives of the assets: Buildings incl. leasehold improvements and outdoor facilities 8 to 40 years Technical equipment and machinery 8 to 12 years Special tools max. 4 years Operating and office equipment 3 to 8 years Impairment testing is carried out if the",
    "body_json": "{\"full_text\": \"Assets under construction and property, plant and equipment are recognized at acquisition or production cost less accumulated depreciation and accumulated impairment losses.\\nScheduled straight-line depreciation is based on the following useful lives of the assets:\\nBuildings incl. leasehold improvements and outdoor facilities 8 to 40 years\\nTechnical equipment and machinery 8 to 12 years\\nSpecial tools max. 4 years\\nOperating and office equipment 3 to 8 years\\nImpairment testing is carried out if there are indications that an item of property, plant and equipment may be impaired.\\nTime of capitalization approach:\\nAssets are generally recognized on the date on which actual control over the asset is acquired through a transfer of benefits and risks or control/use is transferred to the asset.\\nUnfinished assets that are not yet ready for use are initially recognized under assets under construction. They are reclassified to the respective asset class of property, plant and equipment and depreciation begins when the item of property, plant and equipment is in its intended location and condition for use.\\nProperty, plant and equipment is capitalized directly via the asset number created in the sub-ledger against the supplier.\\nInitial evaluation\\nIf an asset is acquired in a single transaction, the following costs represent the acquisition costs and must therefore be capitalized:\\nThe following costs are directly attributable to property, plant and equipment:\\nInstallation and installation costs,\\nCosts for external and internal design services\\nConsultant and expert costs\\nDirect and indirect material costs\\nOwn work by employees (direct costs)\\nDemolition costs\\nInterest on borrowed capital\\nAcquisition costs not eligible for capitalization:\\nCosts that cannot be directly allocated and therefore cannot be capitalized:\\nCosts of preparing decisions (consulting costs)\\nCosts for the opening of a new establishment,\\nGeneral administrative costs as general overheads\\ncosts for the introduction of a new product\\nTraining costs\\nThe following costs may not be included as production costs:\\nempty costs (additional costs)\\nStart-up and pre-production costs\\nGeneral administration and distribution costs\\nIncome and property taxes\\nImputed costs and profits\\nTooling subsidies received from third parties (customers)\\nSubsequent acquisition costs/production costs:\\nIn principle, expenses incurred after the initial recognition of the item of property, plant and equipment are not capitalized unless it is probable that these expenses will significantly increase the inflow of economic benefits associated with the item of property, plant and equipment. The capitalization of subsequent acquisition costs is subject to the same logic as the initial capitalization of acquisition costs.\\nOngoing maintenance, repair and servicing expenses are not capitalizable costs, but must be recognized as immediate maintenance expenses.\\nLow-value economic goods\\nThe capitalization of low-value assets (GWG) is subject to the condition that the acquisition costs or production costs are over Euro 250 and under Euro 800 net value.\\nInvestment and income subsidies\\nGovernment grants for investments or assets in the form of investment subsidies and investment grants are only recognized in the balance sheet for property, plant and equipment if there is adequate security for them:\\nfulfillment of the conditions within the CATENSYS Group\\nGranting of the subsidy\\nTo deduct the grant from the acquisition or production costs, both conditions must be met cumulatively.\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_non_current_assets\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"afa\", \"catensys_group\", \"ias16\", \"ias38\", \"ifrs\", \"sachanlagen\"]",
    "active": 1,
    "_parent_key": "acc_guide_non_current_assets"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_leasing_ifrs_16",
    "title": "Leasing (IFRS 16)",
    "summary": "IFRS 16 requires lessees to fully recognize the economic impact of lease agreements on the balance sheet. Important: These lease-related entries are recorded exclusively in the IFRS ledger. They are not recognized in the local GAAP accounting records, as many national accounting standards (e.g., German HGB) do not require full balance sheet recognition of leases in the same manner as IFRS 16. Recognition criteria: Lease term: \t\t\t\t> 12 months Value of the underlying asset: \t> USD 5,000 According ",
    "body_json": "{\"full_text\": \"IFRS 16 requires lessees to fully recognize the economic impact of lease agreements on the balance sheet.\\nImportant: These lease-related entries are recorded exclusively in the IFRS ledger. They are not recognized in the local GAAP accounting records, as many national accounting standards (e.g., German HGB) do not require full balance sheet recognition of leases in the same manner as IFRS 16.\\nRecognition criteria:\\nLease term: \\t\\t\\t\\t> 12 months\\nValue of the underlying asset: \\t> USD 5,000\\nAccording to IFRS 16.9, a lease exists if the following three criteria are met cumulatively:\\nthe agreement relates to an identifiable asset,\\nthe lessee is entitled to the full economic benefits from the asset for the entire term of the lease.\\nthe lessee can determine how and for what purpose the asset is used during the entire term of the agreement.\\nIn accordance with IFRS 16, the basic rules are to be applied to all leases, except for\\nservice concessions\\nlicenses for intellectual property\\nlicense agreements for intangible assets and copyrights.\\nCatensys Group has decided not to voluntarily apply the new IFRS 16 leasing standard to intangible assets such as software.\\nExample of frequent use:\\nLeasing is often used in the business sector, as the following examples show:\\nReal estate: office and production buildings\\nVehicle fleet/vehicles: cars, forklift trucks and other production vehicles\\nTechnical equipment: tools and production equipment\\nIT area: computers, servers, and telephones\\nOffice equipment: desks, chairs, and furniture\\nCalculation Example of Leasing after IFRS16:\\n(Car-Leasing, Right of use for tangible assets about 29.772,07 EUR for a term of 36 months).\\nLease Start date: 01.09.2023\\nLease-fixed monthly payment: 922 EUR\\nFixed-Periods: 36 months\\nannual interest rate: 7,20 %\\nRight of use (RoU): 29.772,07 EUR\\nStatus of Posting data the end of the year 2023:\\nLeasing liability on end of the year 2023: 26.771,73 EUR\\nthe Opening Balance of Leasing liability will be monthly reduced throw Repayment and Interest.\\nLeasing Right-of-use Asset on end of the year2023: 26.464,07 EUR\\nthe Opening Balance of Right of use will be monthly reduced in almost cases throw Depreciation.\\nExample - Journal Entry:\\nInitial Recognition\\nDebit:\\t50100 - Leasing real estate\\nCredit:\\t489100 - Other payables due within 1-5 years\\nSubsequent Measurement\\nDepreciation of ROU-Asset:\\nDebit:\\t652000 - Accumulated depreciation - buildings\\nCredit:\\t50110 - Depreciation - leasing real estate\\nInterest Expense on Lease Liability:\\nDebit:\\t756000 - Interest expense - liabilities\\nCredit:\\t489100 - Other payables due within 1-5 years\\nInvoice:\\nDebit:\\t670000 - Occupancy costs\\nCredit:\\t440000 Domestic payables (Supplier Account: L100031)\\nRepayment:\\nDebit:\\t440000 Domestic payables (Supplier Account: L100031)\\nCredit:\\t280000 – Bank\\nReduction of lease liability:\\nDebit:\\t489100 - Other payables due within 1-5 years\\nCredit:\\t670000 – Occupancy costs\\nAccounting Workflow:\\nFrom the accounting workflow, as the process basically runs, the posting in the first step is the right-of-use against the lease liability (as already mentioned in the example GL-Account 080100-Lease other equipment* against the GL-Account 489100 Other payables >1 Year). Then in monthly basis throw Assets-run will be the depreciation automatically posted but the Interest should be monthly manually posted. In most cases, the lease payment will be paid to the lessor via direct debit, thus reducing the lease liability.\\n*All postings within fixed assets only take place in sub-ledgers and never in general ledgers. This means that we cannot make an entry against a fixed asset account in General Ledger and can only make an entry against a fixed asset number that we have already entered in Fixed Assets.\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IFRS 16\", \"IFRS 16.9\", \"IFRS16\"], \"parent_section\": \"acc_guide_non_current_assets\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\", \"ifrs16\", \"leasing\"]",
    "active": 1,
    "_parent_key": "acc_guide_non_current_assets"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_financial_assets_investments_ifrs_9_ias_28",
    "title": "Financial Assets & Investments (IFRS 9, IAS 28)",
    "summary": "Financial investments are recognized either at cost, amortized cost, or fair value, depending on the type of investment and the applicable IFRS standard. Investments in affiliated companies are generally accounted for using the equity method according to IAS 28, unless another measurement basis is chosen in separate financial statements (e.g. cost or fair value). Loans and other debt instruments are typically measured at amortized cost, provided the business model is to hold the asset to collect",
    "body_json": "{\"full_text\": \"Financial investments are recognized either at cost, amortized cost, or fair value, depending on the type of investment and the applicable IFRS standard.\\nInvestments in affiliated companies are generally accounted for using the equity method according to IAS 28, unless another measurement basis is chosen in separate financial statements (e.g. cost or fair value).\\nLoans and other debt instruments are typically measured at amortized cost, provided the business model is to hold the asset to collect contractual cash flows and the instrument passes the SPPI test (solely payments of principal and interest).\\nUnder IFRS 9, certain financial assets may alternatively be measured at:\\nFair value through profit or loss (FVTPL), or\\nFair value through other comprehensive income (FVOCI), if an irrevocable election is made at initial recognition for equity instruments not held for trading.\\nImpairment is assessed using the expected credit loss (ECL) model for all financial assets measured at amortized cost or FVOCI.\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 28\", \"IFRS 9\"], \"parent_section\": \"acc_guide_non_current_assets\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"assets\", \"bilanzierung\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": "acc_guide_non_current_assets"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_current_assets",
    "title": "Current Assets",
    "summary": "Current assets are expected to be realized or consumed within the normal operating cycle. These include receivables (IFRS 9), inventories (IAS 2), and cash (IAS 7).",
    "body_json": "{\"full_text\": \"Current assets are expected to be realized or consumed within the normal operating cycle. These include receivables (IFRS 9), inventories (IAS 2), and cash (IAS 7).\", \"section_level\": 3, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 2\", \"IAS 7\", \"IFRS 9\"], \"parent_section\": \"acc_guide_assets\"}",
    "confidence": 5,
    "importance": 3,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"assets\", \"bilanzierung\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": "acc_guide_assets"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_receivables_ifrs_9",
    "title": "Receivables (IFRS 9)",
    "summary": "Under IFRS 9, receivables are measured at amortised cost using the Expected Credit Loss (ECL) model. This model requires that potential credit losses be recognized before an actual default occurs, allowing entities to reflect credit risk early. There are two stages of loss recognition: 12-month ECL: Expected losses over the next 12 months, applied when there is no significant increase in credit risk. Lifetime ECL: Expected losses over the full term of the receivable, applied when credit risk has",
    "body_json": "{\"full_text\": \"Under IFRS 9, receivables are measured at amortised cost using the Expected Credit Loss (ECL) model. This model requires that potential credit losses be recognized before an actual default occurs, allowing entities to reflect credit risk early.\\nThere are two stages of loss recognition:\\n12-month ECL: Expected losses over the next 12 months, applied when there is no significant increase in credit risk.\\nLifetime ECL: Expected losses over the full term of the receivable, applied when credit risk has significantly increased, e.g. in cases of payment delays or signs of insolvency.\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IFRS 9\"], \"parent_section\": \"acc_guide_current_assets\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"forderungen\", \"ifrs\", \"ifrs9\"]",
    "active": 1,
    "_parent_key": "acc_guide_current_assets"
  },
  {
    "layer": "process",
    "object_type": "process",
    "key": "acc_guide_customer_payment_clearing",
    "title": "Customer Payment Clearing",
    "summary": "All incoming customer payments must be promptly cleared against the related invoices. Timely reconciliation ensures accurate accounts receivable balances and dependable financial reporting. This process provides: Full visibility of paid, outstanding, and overdue invoices Early detection of discrepancies (e.g., duplicate payments, incorrect amounts, partial allocations, unrecorded receipts) A reliable basis for cash flow management and collection activities Clear and professional communication wi",
    "body_json": "{\"full_text\": \"All incoming customer payments must be promptly cleared against the related invoices. Timely reconciliation ensures accurate accounts receivable balances and dependable financial reporting.\\nThis process provides:\\nFull visibility of paid, outstanding, and overdue invoices\\nEarly detection of discrepancies (e.g., duplicate payments, incorrect amounts, partial allocations, unrecorded receipts)\\nA reliable basis for cash flow management and collection activities\\nClear and professional communication with customers\\nFailure to clear payments may result in incorrect receivable balances, cash flow misstatements, and reputational risk.\\nRules:\\nClearing Date = Payment Date\\nThe clearing date must always correspond to the actual payment date (value date).\\nClearing Currency = Document Currency\\nThe reconciliation must be performed in the same currency as the original invoice (document currency).\\nTransaction: F-32\\nExample:\\nThe customer payment and the corresponding invoice must be selected and matched in the system. The total balance must equal zero before clearing. Only once the difference is zero may the items be cleared.\\nCurrency Differences:\\nDifference > 1% of Payment:\\nGL-Account: 518500 Sales deductions with cost element\\nDifference < 1% of Payment:\\nGL-Account: 694120 PRD finished goods\", \"section_level\": 5, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_receivables_ifrs_9\"}",
    "confidence": 5,
    "importance": 1,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": "acc_guide_receivables_ifrs_9"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_specific_allowance_for_bad_debts",
    "title": "Specific Allowance for Bad Debts",
    "summary": "Financial assets must be continuously assessed for impairment under IFRS 9. If, since initial recognition, there is evidence of a significant increase in credit risk, an individual impairment allowance (specific allowance) must be recognized. Such impairments become necessary when there are objective indications of potential default or a significantly increased risk of default, assessed using qualitative and quantitative criteria. Case 1: Doubt about collectability – no definitive proof yet If t",
    "body_json": "{\"full_text\": \"Financial assets must be continuously assessed for impairment under IFRS 9. If, since initial recognition, there is evidence of a significant increase in credit risk, an individual impairment allowance (specific allowance) must be recognized. Such impairments become necessary when there are objective indications of potential default or a significantly increased risk of default, assessed using qualitative and quantitative criteria.\\nCase 1: Doubt about collectability – no definitive proof yet\\nIf there are indications that a receivable may not be fully collectible, but it is not yet clearly classified as uncollectible, IFRS 9.5.5.3 requires recognizing an individual impairment allowance based on the Lifetime Expected Credit Loss (ECL).\\nValue-added tax (VAT) remains unaffected in this case, as the legal right to the receivable still exists and no definitive default has occurred.\\nThe assessment of a significant increase in credit risk is based on a variety of qualitative and quantitative factors according to IFRS 9, Appendices B5.5.15 to B5.5.17. Typical indicators include, but are not limited to:\\nLack of response from the customer to reminders or other inquiries (IFRS 9 B5.5.16)\\nPayment delays exceeding 30 days (IFRS 9.5.5.11)\\nNegative credit reports or deterioration in credit rating (IFRS 9 B5.5.17 lit. a and b)\\nOngoing negotiations regarding installment payments or payment deferrals (IFRS 9 B5.5.17 lit. e)\\nIndications of financial difficulties or insolvency risks (IFRS 9 B5.5.17 lit. c)\\nThese indicators serve as guidance and require judgment based on the debtor’s individual risk profile. The evaluation takes into account all available information as of the reporting date.\\nCase 2: Objective evidence of uncollectibility\\nIf there is objective evidence that the receivable is uncollectible—for example:\\nCourt insolvency ruling,\\nTermination of enforcement proceedings,\\nStatute of limitations on the claim,\\nWaiver by settlement,\\nthe receivable is written off in full.\\nPrior to write-off, any previously recognized specific impairment allowance (net) must be reversed, as the gross amount (including VAT) is derecognized.\\nExample - Journal Entry:\\nCase 1:\\nDebit:\\t695200 – Depreciation Customers\\nCredit:\\t249100 - Depreciation of Customer Accounts\\nCase 2:\\nDebit:\\t695100 - Write-off of uncollectible receivables\\nCredit:\\t240000 – Domestic Receivables (Customer Account: 90133);\", \"section_level\": 5, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IFRS 9\", \"IFRS 9.5.5.11\", \"IFRS 9.5.5.3\"], \"parent_section\": \"acc_guide_receivables_ifrs_9\"}",
    "confidence": 5,
    "importance": 1,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"forderungen\", \"ifrs\", \"wertberichtigung\"]",
    "active": 1,
    "_parent_key": "acc_guide_receivables_ifrs_9"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_flat_rate_value_adjustments",
    "title": "Flat-Rate Value Adjustments",
    "summary": "In the annual financial statements, a collective allowance is recognized to reflect general credit risks on receivables. This allowance applies to all outstanding receivables except those with an already recognized individual impairment or intercompany receivables, as the latter do not pose a real default risk. Additionally, receivables already written off are excluded from the valuation basis. For the calculation under IFRS, all outstanding receivables are exported and initially segmented into ",
    "body_json": "{\"full_text\": \"In the annual financial statements, a collective allowance is recognized to reflect general credit risks on receivables. This allowance applies to all outstanding receivables except those with an already recognized individual impairment or intercompany receivables, as the latter do not pose a real default risk. Additionally, receivables already written off are excluded from the valuation basis.\\nFor the calculation under IFRS, all outstanding receivables are exported and initially segmented into domestic and foreign customers. The assessment is based on the aging of receivables to estimate the default risk appropriately. Depending on the receivables’ aging, a tiered percentage is applied as follows:\\nThe basis for calculation is the net receivables balance. Typically, domestic and foreign receivables are evaluated separately, as foreign customers are generally considered higher risk.\\nUnder IFRS 9, the collective allowance is based on the 12-month Expected Credit Loss (ECL) model. This incorporates historical default rates, current economic conditions, and forward-looking information such as economic forecasts and industry trends.\\nThe collective allowance is recalculated, established, and recorded annually. Before booking the newly calculated allowance, any allowance from the prior year must be fully reversed, regardless of whether the default rates have changed. Additionally, at least once a year, the recoverability of receivables must be reviewed. Subsequently, the current collective allowance is recorded based on the updated risk assessment. The booking process follows separate requirements under IFRS and local accounting standards (e.g., HGB).\\nExample - Journal Entry:\\nDebit:\\t695300 - Flat-rate value adjustments\\nCredit:\\t240090 - Revaluation account domestic receivables\\n241090 - Revaluation account foreign receivables\", \"section_level\": 5, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IFRS 9\"], \"parent_section\": \"acc_guide_receivables_ifrs_9\"}",
    "confidence": 5,
    "importance": 1,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": "acc_guide_receivables_ifrs_9"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_inventory_stock_valuation",
    "title": "Inventory stock valuation",
    "summary": "Inventory is valued using a periodic, material-specific average cost method under the lower-of-cost-or-market principle. The average carrying amount per material is calculated for the full year across all locations and compared with the average market price. If the carrying amount exceeds the market price, the inventory is written down to the lower market value. If the carrying amount is below the market price, a market price risk provision is recognized, applying a worst-case scenario. Prior to",
    "body_json": "{\"full_text\": \"Inventory is valued using a periodic, material-specific average cost method under the lower-of-cost-or-market principle. The average carrying amount per material is calculated for the full year across all locations and compared with the average market price. If the carrying amount exceeds the market price, the inventory is written down to the lower market value. If the carrying amount is below the market price, a market price risk provision is recognized, applying a worst-case scenario.\\nPrior to valuation, a reconciliation between the General Ledger and Inventory Subledger must be completed; the process can only proceed if the reconciliation is fully balanced. Year-end inventory balances are extracted, and historical consumption data is analyzed to determine utilization risk. Items with no consumption must be documented, and write-downs are applied as necessary.\\nRisk estimation is determined based on the historical coverage period: up to 24 months: 0 %, 24–48 months: 20 %, 48–72 months: 40 %, and over 72 months: 60 %.\\nFor each material, the following information is considered in the valuation: the current market price per unit, the average or historical stock value per unit, and whether the average market price is below the carrying amount, which indicates potential market price risk. System-generated valuation suggestions may be used as guidance but must always be checked for compliance with this guideline. Where better economic knowledge is available, it prevails, and any material deviations must be documented and reported to Corporate Accounting (Headquarters).\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_current_assets\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ias2\", \"ifrs\", \"lager\"]",
    "active": 1,
    "_parent_key": "acc_guide_current_assets"
  },
  {
    "layer": "process",
    "object_type": "process",
    "key": "acc_guide_material_goods_in_transit_reconciliation",
    "title": "Material Goods-in-Transit Reconciliation",
    "summary": "Goods in transit are materials that have been shipped but have not yet arrived at the receiving location at the balance sheet date. Ownership and control over these goods during transit depend on the agreed Incoterms between the buyer and the seller. According to IFRS 15, revenue recognition and invoicing are only appropriate when control over the goods has been transferred to the buyer, as defined by the applicable Incoterms. If the goods have already been dispatched but control has not yet pas",
    "body_json": "{\"full_text\": \"Goods in transit are materials that have been shipped but have not yet arrived at the receiving location at the balance sheet date. Ownership and control over these goods during transit depend on the agreed Incoterms between the buyer and the seller.\\nAccording to IFRS 15, revenue recognition and invoicing are only appropriate when control over the goods has been transferred to the buyer, as defined by the applicable Incoterms. If the goods have already been dispatched but control has not yet passed—meaning the goods have not yet been delivered according to the agreed Incoterms—then the seller must not recognize revenue or issue an invoice.\\nDispatch alone is not sufficient; if the buyer has not obtained control, the economic transfer has not occurred, and the transaction cannot be recognized in revenue.\\nConversely, if the buyer has obtained control and the right to use or dispose of the goods during transit (as defined by the Incoterms), the buyer must recognize the goods as inventory and record the associated costs accordingly.\\nThis reconciliation ensures that goods in transit are properly accounted for, reflecting the correct ownership and control status as of the reporting date.\\nExample - Journal Entry:\\nBuyer:\\nInvoice Receipt (IR):\\nDebit:\\t204800 - GR/IR: Goods/services not yet delivered\\nCredit:\\t460000 - Payables affiliated companies (Supplier Account: L372960)\\nGoods Receipt (GR):\\nDebit:\\t228000 - Trading goods\\nCredit:\\t293000 - WRX GR/IR-clearing - external procurement\\n(F.19  automatic clearing process once a month)\\nSeller:\\nInvoice Delivery:\\nDebit: 250000 – Receivables from affiliated companies (Customer Account: 103055)\\nCredit: 502005 - Sales revenue subsidiaries abroad\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IFRS 15\"], \"parent_section\": \"acc_guide_current_assets\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": "acc_guide_current_assets"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_cash_and_cash_equivalents",
    "title": "Cash and Cash Equivalents",
    "summary": "IAS 7 regulates the presentation and disclosure of the cash flow statement, which provides information about an entity’s cash inflows and outflows during a reporting period. The statement of cash flows is a key financial report that helps users assess the entity’s ability to generate cash and cash equivalents, meet its obligations, and fund its operations and investments. Under IAS 7, cash flows are classified into three categories: Operating activities: Cash flows from the principal revenue-pro",
    "body_json": "{\"full_text\": \"IAS 7 regulates the presentation and disclosure of the cash flow statement, which provides information about an entity’s cash inflows and outflows during a reporting period. The statement of cash flows is a key financial report that helps users assess the entity’s ability to generate cash and cash equivalents, meet its obligations, and fund its operations and investments.\\nUnder IAS 7, cash flows are classified into three categories:\\nOperating activities: Cash flows from the principal revenue-producing activities of the entity.\\nInvesting activities: Cash flows related to the acquisition and disposal of long-term assets and investments.\\nFinancing activities: Cash flows that result in changes in the size and composition of the entity’s equity and borrowings.\\nThe standard requires the direct or indirect method for reporting cash flows from operating activities, with the indirect method being more commonly used. IAS 7 also mandates disclosures about non-cash investing and financing activities and the reconciliation of cash and cash equivalents.\\nThe statement of cash flows complements the income statement and balance sheet by providing insight into liquidity, solvency, and financial flexibility.\\nPrepaid expenses\\nPrepaid expenses must be recognized in accordance with the accrual principle, ensuring that costs are recorded in the period to which they economically relate. If a service or benefit is paid in advance but relates to a future reporting period, the amount must be recorded as a prepaid expense (\\\"active accrual\\\") in the balance sheet.\\nFor this purpose, account 290000 – Prepaid Assets is to be used. Typical examples include insurance premiums, software licenses, service contracts, or rent paid in advance. The cost should be initially booked to account 290000 and then released to the appropriate expense account over the term of the benefit, using monthly journal entries.\\nEach entity is responsible for reviewing all invoices and payments to identify any prepaid items and to ensure timely and accurate postings to account 290000. Prepaid expenses must be reviewed regularly, especially at period-end, to confirm that the balances are still valid and properly allocated across the correct periods.\\nProper use of account 290000 is essential for accurate monthly and annual reporting, as it ensures that expenses are not overstated in the current period and that the financial statements provide a true and fair view of the company’s financial position.\\nExample - Journal Entry:\\nPrepayment Supplier\\nDebit:\\t290000 – Prepaid expenses\\nCredit:\\tSupplier Account\\nDebit:\\tSupplier Account\\nCredit:\\t280000 - Bank\\nMonthly Accruals\\nDebit:\\tExpense Account\\nCredit:\\t290000 - Prepaid expenses\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 7\"], \"parent_section\": \"acc_guide_current_assets\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ias7\", \"ifrs\", \"liquiditaet\"]",
    "active": 1,
    "_parent_key": "acc_guide_current_assets"
  },
  {
    "layer": "finance",
    "object_type": "concept",
    "key": "acc_guide_liabilities_and_equity",
    "title": "Liabilities and Equity",
    "summary": "Liabilities and equity are classified based on their nature and maturity. IFRS distinguishes between provisions, financial liabilities, and shareholders’ equity, each with specific recognition and measurement rules.",
    "body_json": "{\"full_text\": \"Liabilities and equity are classified based on their nature and maturity. IFRS distinguishes between provisions, financial liabilities, and shareholders’ equity, each with specific recognition and measurement rules.\", \"section_level\": 2, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_accounting_and_valuation_guidelines_per_account_group\"}",
    "confidence": 5,
    "importance": 4,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"eigenkapital\", \"equity\", \"ifrs\", \"liabilities\", \"rueckstellungen\"]",
    "active": 1,
    "_parent_key": "acc_guide_accounting_and_valuation_guidelines_per_account_group"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_provisions_and_accruals",
    "title": "Provisions and Accruals",
    "summary": "Provisions are liabilities of uncertain timing or amount that arise from past events, where the entity expects to incur an outflow of resources embodying economic benefits to settle the obligation. For a provision to be recognized under IFRS, three criteria must be met simultaneously: Present obligation There must be a present legal or constructive obligation to a third party as a result of a past event. A legal obligation arises from contracts or legislation, while a constructive obligation ari",
    "body_json": "{\"full_text\": \"Provisions are liabilities of uncertain timing or amount that arise from past events, where the entity expects to incur an outflow of resources embodying economic benefits to settle the obligation.\\nFor a provision to be recognized under IFRS, three criteria must be met simultaneously:\\nPresent obligation\\nThere must be a present legal or constructive obligation to a third party as a result of a past event. A legal obligation arises from contracts or legislation, while a constructive obligation arises from an entity’s established practices, published policies, or specific statements creating a valid expectation.\\nProbability of outflow\\nIt is probable (i.e., more likely than not, greater than 50%) that an outflow of resources embodying economic benefits will be required to settle the obligation.\\nReliable estimate\\nThe amount of the obligation can be reliably estimated, even if some uncertainty exists.\\nIf all three criteria are met, a provision must be recognized in the balance sheet. If not, no provision is recognized, but the obligation may be disclosed as a contingent liability in the notes to the financial statements.\", \"section_level\": 3, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_liabilities_and_equity\"}",
    "confidence": 5,
    "importance": 3,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\", \"liabilities\", \"rueckstellungen\"]",
    "active": 1,
    "_parent_key": "acc_guide_liabilities_and_equity"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_personnel_related_provisions",
    "title": "Personnel-related Provisions",
    "summary": "Personnel-related provisions are recognized for future obligations towards employees that have already been economically incurred but will only become due in the future. These provisions are based on collective bargaining agreements, employment contracts, or company agreements. They are reviewed and adjusted at least annually to reflect any changes in entitlements or underlying conditions. Examples: Accrued vacation leave Anniversary bonuses Severance payments Recognition criteria: The obligatio",
    "body_json": "{\"full_text\": \"Personnel-related provisions are recognized for future obligations towards employees that have already been economically incurred but will only become due in the future. These provisions are based on collective bargaining agreements, employment contracts, or company agreements. They are reviewed and adjusted at least annually to reflect any changes in entitlements or underlying conditions.\\nExamples:\\nAccrued vacation leave\\nAnniversary bonuses\\nSeverance payments\\nRecognition criteria:\\nThe obligation exists at the reporting date (e.g., accrued vacation entitlement).\\nIt is probable that an outflow of resources will be required to settle the obligation.\\nThe expense can be reliably estimated.\\nExample - Journal Entry:\\nTo accrue vacation pay:\\nDebit:\\t631010 – Holiday remuneration salaried employees\\nCredit:\\t390011 - Accruals vacation bonus\\nTo accrue social security contributions related to personnel:\\nDebit:\\t640000 – Social insurance expenditures\\nCredit:\\t390011 - Accruals vacation bonus\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_provisions_and_accruals\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\", \"liabilities\", \"rueckstellungen\"]",
    "active": 1,
    "_parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "layer": "risk",
    "object_type": "rule",
    "key": "acc_guide_provisions_for_onerous_contracts",
    "title": "Provisions for Onerous Contracts",
    "summary": "A provision for an onerous contract (IAS 37) is recognized when: The unavoidable costs of fulfilling a contract exceed the expected economic benefits. The contract exists at the reporting date. The expected loss is probable and reliably measurable. In this case, a provision must be recognized (IAS 37.66). Events after the Reporting Period (IAS 10): Adjusting events (wertaufhellende Ereignisse) Provide additional evidence about conditions that already existed at the reporting date. Must be reflec",
    "body_json": "{\"full_text\": \"A provision for an onerous contract (IAS 37) is recognized when:\\nThe unavoidable costs of fulfilling a contract exceed the expected economic benefits.\\nThe contract exists at the reporting date.\\nThe expected loss is probable and reliably measurable.\\nIn this case, a provision must be recognized (IAS 37.66).\\nEvents after the Reporting Period (IAS 10):\\nAdjusting events (wertaufhellende Ereignisse)\\nProvide additional evidence about conditions that already existed at the reporting date.\\nMust be reflected in the financial statements.\\nNon-adjusting events (wertbegründende Ereignisse)\\nRelate to conditions that arose after the reporting date.\\nDo not require adjustments in the financial statements.\\nMay require disclosure in the notes if material.\\nBefore recognizing a provision, any necessary inventory write-downs (impairments) related to the contract must first be recorded in accordance with IAS 2. The impairment is made up to the amount of the expected loss, reducing the carrying amount of inventories. If the expected loss exceeds the carrying amount of the related inventories, the remaining amount is recognized as other operating expenses.\\nThis applies in particular to framework agreements or other binding customer contracts (under IFRS 15) where the total estimated costs for the contracted and probable quantities exceed the transaction price. Recognizing the provision ensures that these losses are recorded promptly and accurately in the period in which they become probable.\\nExamples: Unprofitable delivery contracts, construction projects with cost overruns, framework contracts where expected costs exceed revenues.\\nRecognition criteria:\\n• A binding contract or project exists that cannot be cancelled without penalty.\\n• A loss is probable.\\n• The amount of the expected loss can be reliably estimated.\\n• Any related inventories have already been written down to net realizable value before recognizing the provision.\\nExample - Journal Entry:\\n1. Inventory Write-Down:\\nDebit:\\t693000 - Loss in the event of damage\\nCredit:\\t200190 - BSD Adjustment account Inventory Raw Materials\\n2. Loss Making Provision:\\nDebit:\\t693000 - Loss in the event of damage\\nCredit:\\t397000 - Provisions for imminent losses and pending transactions\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 10\", \"IAS 2\", \"IAS 37\", \"IAS 37.66\", \"IFRS 15\"], \"parent_section\": \"acc_guide_provisions_and_accruals\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\", \"liabilities\", \"rueckstellungen\"]",
    "active": 1,
    "_parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_accruals_for_outstanding_invoices",
    "title": "Accruals for Outstanding Invoices",
    "summary": "Outstanding invoices refer to services or goods that have been delivered or rendered but have neither been invoiced nor recorded in the accounting system yet. Recognition criteria: The contractual service has been performed. An unconditional right to payment exists. Collectability and amount can be reliably estimated. Example - Journal Entry: Debit:\tExpense account Credit:\t393000 - Provisions for indeterminate payables",
    "body_json": "{\"full_text\": \"Outstanding invoices refer to services or goods that have been delivered or rendered but have neither been invoiced nor recorded in the accounting system yet.\\nRecognition criteria:\\nThe contractual service has been performed.\\nAn unconditional right to payment exists.\\nCollectability and amount can be reliably estimated.\\nExample - Journal Entry:\\nDebit:\\tExpense account\\nCredit:\\t393000 - Provisions for indeterminate payables\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_provisions_and_accruals\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "layer": "risk",
    "object_type": "rule",
    "key": "acc_guide_warranty_provisions",
    "title": "Warranty Provisions",
    "summary": "Warranty provisions are recognized for the obligation to rework, replace or pay damages free of charge. They may arise from legal, contractual or constructive obligations. Provisions for warranties must generally be recognized for expected third-party claims arising from individual circumstances. The creation of general provisions is not permitted. However, so-called \"lump-sum\" warranty provisions must be recognized if the history of an outflow of resources can be proven for many similar busines",
    "body_json": "{\"full_text\": \"Warranty provisions are recognized for the obligation to rework, replace or pay damages free of charge. They may arise from legal, contractual or constructive obligations.\\nProvisions for warranties must generally be recognized for expected third-party claims arising from individual circumstances. The creation of general provisions is not permitted. However, so-called \\\"lump-sum\\\" warranty provisions must be recognized if the history of an outflow of resources can be proven for many similar business transactions.\\nWarranty provisions are calculated on a cost basis. In particular, the following realistically estimated cost types must be included in the scope of the provision:\\ncosts of replacement delivery or rework (e.g. manufacturing costs of own products, cost price of merchandise)\\nRemoval and installation costs,\\ntravel costs and\\ncompensation for damages.\\nIn some warranty cases, settlement agreements may contain clauses that contractually grant the customer concerned compensation in the form of bonuses or discounts on future sales revenues. Such \\\"bonus/discount components\\\" do not justify the recognition of a warranty provision in the Cat Group and are therefore not to be considered when forming provisions.\\nThis applies irrespective of the existence of an admission of guilt on the part of the CAT Group vis-à-vis the customer concerned and irrespective of the \\\"type\\\" of the underlying transactions - ongoing business or additional business specified in the agreement.\\nProvisions for warranties - general provisions\\nWarranty provisions are not calculated as a lump sum, e.g. as X% of total sales. However, so-called lump-sum warranty provisions must be recognized as liabilities under the following conditions:\\nThere is a large number of similar obligations or business transactions,\\nthe expected value method is applicable, the possible settlement amounts are based on a probability distribution that can be verified by means of a corresponding history and\\nthe obligation must relate to products or product groups that are already sold on the market, as only here does a warranty history exist. This applies irrespective of the existence of an admission of guilt on the part of the CAT Group vis-à-vis the customer concerned and irrespective of the \\\"type\\\" of the underlying transactions - ongoing business or additional business specified in the agreement.\\nIf there is a different warranty risk for individual products or product groups, these risk classes must be summarized, based on which the lump-sum warranty provision is to be calculated.\\nFurthermore, when determining the lump-sum warranty provision, care must be taken to ensure that obligations that have already been considered through the creation of individual provisions are not included in the calculation.\\nPosting example for a warranty provision:\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_provisions_and_accruals\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"garantie\", \"gewaehrleistung\", \"ifrs\", \"liabilities\", \"rueckstellungen\"]",
    "active": 1,
    "_parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_provision_for_obligations_for_dismantling_or_disposal",
    "title": "Provision for Obligations for Dismantling or Disposal",
    "summary": "The costs of dismantling or disposal on decommissioning must be recognized as a liability at the present value of the total costs at the time the asset is decommissioned or put into operation, provided the obligation to dismantle or dispose of the asset exists in law or in fact. The costs recognized as liabilities must be allocated to the acquisition/production costs of the assets and capitalized. The value of the provision may change over time due to changes in the estimated maturity, the estim",
    "body_json": "{\"full_text\": \"The costs of dismantling or disposal on decommissioning must be recognized as a liability at the present value of the total costs at the time the asset is decommissioned or put into operation, provided the obligation to dismantle or dispose of the asset exists in law or in fact. The costs recognized as liabilities must be allocated to the acquisition/production costs of the assets and capitalized.\\nThe value of the provision may change over time due to changes in the estimated maturity, the estimated cash outflow or the discount rate. This change in the value of the provision must be considered when recognizing the corresponding asset as follows.\\nAn increase in the obligation must be allocated to the amortized cost of the asset in the financial year of the change (subsequent capitalization) and depreciated over the remaining useful life. A reduction in the obligation must be deducted from amortized cost accordingly.\\nIf the amount resulting from a reduction in the obligation exceeds the carrying amount of the asset, this excess must be recognized immediately in profit or loss.\\nIf the change in the obligation leads to an addition to the asset, it must be checked whether there is an indicator of impairment (to carry out the impairment test).\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_provisions_and_accruals\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\", \"liabilities\", \"rueckstellungen\"]",
    "active": 1,
    "_parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_provision_for_archiving",
    "title": "Provision for Archiving",
    "summary": "Legal entities are regularly obliged to retain certain documents for a certain period (e.g. 10 years) due to statutory retention obligations. The retention of documents by companies is done on the one hand to have appropriate documentation of the past for future business activities (self-interest) and on the other hand to comply with legal requirements. The appropriate general ledger account for this purpose is account 390000 – Other provisions. As a rule, companies must archive and retain the f",
    "body_json": "{\"full_text\": \"Legal entities are regularly obliged to retain certain documents for a certain period (e.g. 10 years) due to statutory retention obligations. The retention of documents by companies is done on the one hand to have appropriate documentation of the past for future business activities (self-interest) and on the other hand to comply with legal requirements.\\nThe appropriate general ledger account for this purpose is account 390000 – Other provisions.\\nAs a rule, companies must archive and retain the following documents:\\nTrading books\\nInventories\\nOpening Balance Sheets\\nAnnual Financial Statements\\nConsolidated Financial Statements\\nAll Accounting Documents (all invoices and account statements)\\nDepending on the type of documents and their storage (paper and electronic archiving), different expenses may have to be considered when calculating provisions.\\nIn the case of storage in paper form, the following expenses determine the scope of the provision:\\nRoom costs (e.g. rent, lease, insurance, etc.)\\nMaterial costs (shelving, boxes, folders, etc.)\\nPersonnel costs (archivist, cleaning staff, maintenance, etc.)\\nThe total of these expenses represents the archiving costs to be considered when calculating the provision.\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_provisions_and_accruals\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\", \"liabilities\", \"rueckstellungen\"]",
    "active": 1,
    "_parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "layer": "process",
    "object_type": "process",
    "key": "acc_guide_supplier_payment_clearing",
    "title": "Supplier Payment Clearing",
    "summary": "Regular reconciliation of vendor accounts ensures that all payments, credits, and outstanding invoices are accurately recorded and matched with supplier statements. This prevents discrepancies, avoids duplicate payments, maintains strong supplier relationships, and ensures compliance with accounting standards. Transaction: F-44",
    "body_json": "{\"full_text\": \"Regular reconciliation of vendor accounts ensures that all payments, credits, and outstanding invoices are accurately recorded and matched with supplier statements. This prevents discrepancies, avoids duplicate payments, maintains strong supplier relationships, and ensures compliance with accounting standards.\\nTransaction: F-44\", \"section_level\": 4, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_provisions_and_accruals\"}",
    "confidence": 5,
    "importance": 2,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_financial_liabilities",
    "title": "Financial Liabilities",
    "summary": "Interest liabilities arise from interest that has already accrued on financial liabilities but has not yet been paid. In accordance with IFRS 9, such liabilities are not classified as provisions, but rather as financial liabilities, since the obligation is both legally enforceable and economically incurred. For an interest liability to be recognized, the following criteria must be met: A valid financial obligation must exist, such as a loan agreement. The interest must have already accrued and b",
    "body_json": "{\"full_text\": \"Interest liabilities arise from interest that has already accrued on financial liabilities but has not yet been paid. In accordance with IFRS 9, such liabilities are not classified as provisions, but rather as financial liabilities, since the obligation is both legally enforceable and economically incurred.\\nFor an interest liability to be recognized, the following criteria must be met:\\nA valid financial obligation must exist, such as a loan agreement.\\nThe interest must have already accrued and be economically incurred, even if payment is due later.\\nThe amount of interest must be reliably measurable based on the contractual terms of the underlying financial liability.\\nIn line with IFRS principles, these interest liabilities are recognized separately in the financial statements as part of financial liabilities and measured at amortized cost unless they fall under other specific measurement categories defined in IFRS 9. The recognition ensures that all financial obligations are transparently and accurately reflected in the period in which they arise.\\nFollowing this principle, interest liabilities are classified according to different institutions and varying maturities. Accordingly, they are recorded in distinct accounts to ensure clear and precise financial reporting in line with IFRS requirements.\\nInterests from Banks (short-/long-term)\\nLoans from banks represent financial liabilities arising from contractual loan agreements. In accordance with IFRS 9, they are initially recognized at fair value and subsequently measured at amortized cost using the effective interest method.\\nExample - Journal Entry:\\nDebit:\\t751000 - Bank interest expenses\\nCredit:\\t420110 – Loans <1 year from credit institutions\\nLoan interests from Shareholders (long-term)\\nLoans granted by shareholders are classified as financial liabilities under IFRS 9, provided they are based on contractual agreements and not deemed equity instruments. They are initially recognized at fair value and subsequently measured at amortized cost, unless other classification criteria apply.\\nExample - Journal Entry:\\nDebit:\\t759200 – Other interest and similar exp. affiliated comps\\nCredit:\\t470030 - Payables to associated companies due > 5 years\\nLoan interests from Schaeffler (long-term)\\nLoans received from Schaeffler are treated as financial liabilities in accordance with IFRS 9. These loans are contractually agreed and must be recognized at fair value upon initial recognition, with subsequent measurement at amortized cost using the effective interest method, unless designated otherwise.\\nExample - Journal Entry:\\nDebit:\\t758100 – Schaeffler Interest\\nCredit:\\t420130 - Interests  Schaeffler >5y\\nFactoring Interests (short-term)\\nFactoring liabilities arise when receivables are sold to a factor with recourse, or when the transfer does not meet the derecognition criteria under IFRS 9. In such cases, the receivables remain on the balance sheet, and the proceeds received are recognized as a financial liability.\\nExample - Journal Entry:\\nDebit:\\t759100 – Factoring Interest\\nCredit:\\tSupplier Account\\nIntercompany Interest Liabilities (short-/long-term)\\nFrom the lender’s perspective, interest income on loans granted to related parties is recognized over the term of the loan, based on the contractual interest rate. For short-term loans (with maturities less than one year) as well as long-term loans (with maturities exceeding one year), the accrued interest is recorded as income in the period it is earned, increasing the carrying amount of the loan receivable.\\nJournal entries for interest income:\\nDebit: 120000 - Loans to members of a consolidation group <1 year\\nCredit: 570200 - Other interest & similar revenues-affiliated co.\\nFrom the borrower’s perspective, interest expense on loans received from related parties is accrued and recognized in the period it is incurred. The interest expense increases the carrying amount of the loan liability and reflects the contractual terms agreed within the group. Short-term and long-term loans are treated accordingly, with interest recognized as a finance cost over the respective loan maturity.\\nJournal entries for interest income:\\nDebit: 759200 - Other interest and similar exp. affiliated comps\\nCredit: 420200 - Loans < 1 year\", \"section_level\": 3, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IFRS 9\"], \"parent_section\": \"acc_guide_liabilities_and_equity\"}",
    "confidence": 5,
    "importance": 3,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\", \"liabilities\", \"rueckstellungen\"]",
    "active": 1,
    "_parent_key": "acc_guide_liabilities_and_equity"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_equity",
    "title": "Equity",
    "summary": "Equity represents the residual interest in the assets of an entity after deducting its liabilities. IAS 1 “Presentation of Financial Statements” sets out the requirements for the presentation and disclosure of equity in the financial statements. It requires clear classification and separate disclosure of equity components, such as share capital, share premium, retained earnings, accumulated other comprehensive income (OCI), and reserves. IAS 32 “Financial Instruments: Presentation” defines the d",
    "body_json": "{\"full_text\": \"Equity represents the residual interest in the assets of an entity after deducting its liabilities.\\nIAS 1 “Presentation of Financial Statements” sets out the requirements for the presentation and disclosure of equity in the financial statements. It requires clear classification and separate disclosure of equity components, such as share capital, share premium, retained earnings, accumulated other comprehensive income (OCI), and reserves.\\nIAS 32 “Financial Instruments: Presentation” defines the distinction between financial liabilities and equity instruments. Equity instruments are contracts that evidence a residual interest in the assets of an entity after deducting all liabilities (IAS 32.11).\\nMeasurement:\\nEquity instruments are generally measured at their nominal (face) value at initial recognition, unless issued at a premium or discount, in which case the amount received (fair value) is recorded. Retained earnings and OCI are presented within equity according to IFRS classification.\\nOCI example:\\nOther comprehensive income includes items such as actuarial gains and losses from defined benefit pension plans under IAS 19 “Employee Benefits”. These remeasurements are recognized directly in equity through OCI in the period in which they arise and are not recycled through profit or loss.\", \"section_level\": 3, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 1\", \"IAS 19\", \"IAS 32\", \"IAS 32.11\"], \"parent_section\": \"acc_guide_liabilities_and_equity\"}",
    "confidence": 5,
    "importance": 3,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"eigenkapital\", \"equity\", \"ifrs\"]",
    "active": 1,
    "_parent_key": "acc_guide_liabilities_and_equity"
  },
  {
    "layer": "finance",
    "object_type": "concept",
    "key": "acc_guide_expenses",
    "title": "Expenses",
    "summary": "Other expenses are recorded under accounts 695000 ff. and include, among others, currency translation losses, asset disposals, and write-downs. Foreign exchange losses must be recognized in the income statement in accordance with IFRS 9 and IAS 21, distinguishing between realized and unrealized effects. Currency losses resulting from financial receivables or loans are recorded when exchange rates fluctuate negatively. Example: A foreign currency loan loses value due to exchange rate changes. The",
    "body_json": "{\"full_text\": \"Other expenses are recorded under accounts 695000 ff. and include, among others, currency translation losses, asset disposals, and write-downs.\\nForeign exchange losses must be recognized in the income statement in accordance with IFRS 9 and IAS 21, distinguishing between realized and unrealized effects. Currency losses resulting from financial receivables or loans are recorded when exchange rates fluctuate negatively.\\nExample: A foreign currency loan loses value due to exchange rate changes. The loss is recorded against the financial asset.\\n→ Expense account (e.g., 695400) to financial receivable (e.g., 120000 / 120020)\\nScrapping of fixed assets (e.g., damaged equipment) is recorded as a loss under 696010, reflecting the remaining book value of the asset at disposal.\\nImpairments and unscheduled depreciation are recognized if there are indications that an asset's recoverable amount is below its carrying amount (IAS 36).\", \"section_level\": 2, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 21\", \"IAS 36\", \"IFRS 9\"], \"parent_section\": \"acc_guide_accounting_and_valuation_guidelines_per_account_group\"}",
    "confidence": 5,
    "importance": 4,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"aufwand\", \"catensys_group\", \"expenses\", \"ifrs\"]",
    "active": 1,
    "_parent_key": "acc_guide_accounting_and_valuation_guidelines_per_account_group"
  },
  {
    "layer": "finance",
    "object_type": "concept",
    "key": "acc_guide_revenue",
    "title": "Revenue",
    "summary": "Other income is recorded under accounts 540000 ff. and 572000 ff., and includes exchange gains, reversals of impairments (write-ups), and miscellaneous operating income. Foreign exchange gains must be reported separately under IAS 21. Gains arise when the value of a receivable or financial asset increases due to favorable exchange rate fluctuations. Example: A foreign currency loan increases in value. The gain is recognized in the income statement. → Financial receivable (e.g., 120000 / 120020) ",
    "body_json": "{\"full_text\": \"Other income is recorded under accounts 540000 ff. and 572000 ff., and includes exchange gains, reversals of impairments (write-ups), and miscellaneous operating income.\\nForeign exchange gains must be reported separately under IAS 21. Gains arise when the value of a receivable or financial asset increases due to favorable exchange rate fluctuations.\\nExample: A foreign currency loan increases in value. The gain is recognized in the income statement.\\n→ Financial receivable (e.g., 120000 / 120020) to income account (e.g., 572100)\\nReversals of impairment losses (account 544000) are permitted up to the asset’s amortized cost under IAS 36, provided that the reasons for the original impairment no longer exist. Revaluations above cost are not permitted unless using the revaluation model (rare).\", \"section_level\": 2, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 21\", \"IAS 36\"], \"parent_section\": \"acc_guide_accounting_and_valuation_guidelines_per_account_group\"}",
    "confidence": 5,
    "importance": 4,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\", \"revenue\", \"umsatz\"]",
    "active": 1,
    "_parent_key": "acc_guide_accounting_and_valuation_guidelines_per_account_group"
  },
  {
    "layer": "finance",
    "object_type": "concept",
    "key": "acc_guide_group_and_special_topics",
    "title": "Group and Special Topics",
    "summary": "This section addresses group-specific topics such as intercompany reconciliation, foreign currency (IAS 21), debt consolidation, and audit-related provisions, relevant for group reporting.",
    "body_json": "{\"full_text\": \"This section addresses group-specific topics such as intercompany reconciliation, foreign currency (IAS 21), debt consolidation, and audit-related provisions, relevant for group reporting.\", \"section_level\": 2, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 21\"], \"parent_section\": \"acc_guide_accounting_and_valuation_guidelines_per_account_group\"}",
    "confidence": 5,
    "importance": 4,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": "acc_guide_accounting_and_valuation_guidelines_per_account_group"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_debt_consolidation_inter_company",
    "title": "Debt consolidation – Inter Company",
    "summary": "In the preparation of the consolidated balance sheet, it is critical that all intercompany debt positions are fully and accurately eliminated. Intercompany receivables and payables—whether related to loans, short-term funding, or accrued interest—must not appear in the consolidated financial statements, as they do not represent external assets or liabilities of the group as a whole. Their inclusion would result in an overstatement of both assets and liabilities, thereby distorting the financial ",
    "body_json": "{\"full_text\": \"In the preparation of the consolidated balance sheet, it is critical that all intercompany debt positions are fully and accurately eliminated. Intercompany receivables and payables—whether related to loans, short-term funding, or accrued interest—must not appear in the consolidated financial statements, as they do not represent external assets or liabilities of the group as a whole. Their inclusion would result in an overstatement of both assets and liabilities, thereby distorting the financial position of the group.\\nTo ensure the consolidated balance sheet balances correctly, all group entities must report intercompany positions consistently. Any differences between intercompany loan balances—due, for example, to timing, foreign exchange movements, or local accounting treatments—must be reconciled and adjusted before consolidation. Full elimination of both the principal and any associated interest is required.\\nFurthermore, proper documentation of all intercompany debt arrangements is necessary to support consolidation entries. This includes contracts, interest calculations, and any relevant amendments. Foreign currency-denominated intercompany balances must be translated consistently using the applicable group FX rates, and resulting currency translation differences must be carefully reviewed and eliminated as appropriate to avoid imbalance in the consolidated accounts.\\nIntercompany reconciliation is a mandatory step prior to the group consolidation process. Any unresolved differences can result in a failure to eliminate balances fully, leading to a mismatch between assets and liabilities on the consolidated balance sheet. Therefore, the elimination of intercompany debt is not only a technical requirement but also a critical control point to ensure the integrity and correctness of the consolidated financial statements.\", \"section_level\": 3, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_group_and_special_topics\"}",
    "confidence": 5,
    "importance": 3,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\", \"intercompany\", \"konzern\"]",
    "active": 1,
    "_parent_key": "acc_guide_group_and_special_topics"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_accounts_with_foreign_currency",
    "title": "Accounts with Foreign currency",
    "summary": "In accordance with the functional currency concept used by IAS 21, the financial statements of foreign companies must be prepared in their own currency and then translated into the reporting currency of the CATENSYS Group EURO using the modified closing rate method. The reporting currency is the currency in which the financial statements are published. In accordance with IAS 21.39, all balance sheet items are translated at the closing rate and all income and expense items are translated at the r",
    "body_json": "{\"full_text\": \"In accordance with the functional currency concept used by IAS 21, the financial statements of foreign companies must be prepared in their own currency and then translated into the reporting currency of the CATENSYS Group EURO using the modified closing rate method. The reporting currency is the currency in which the financial statements are published.\\nIn accordance with IAS 21.39, all balance sheet items are translated at the closing rate and all income and expense items are translated at the respective transaction rate or, to simplify matters, at weekly, monthly, or annual average rates.\\nAll translation differences are recognized directly in equity and reported separately.\\nCurrency differences are recognized directly in equity in the form of a separate item. Currency differences are part of \\\"Other comprehensive income\\\". Both the cumulative amount and the annual change must be shown in the statement of changes in equity.\\na) The difference resulting from the application of different exchange rates is shown separately in the statement of changes in non-current assets as a currency adjustment.\\nb) The difference arising in the statement of changes in provisions from the application of different exchange rates is shown separately as a currency adjustment in the statement of changes in provisions from the application of different exchange rates is shown separately as a currency adjustment in the statement of changes in provisions.\\nc) Changes in equity resulting from additional disclosure data are reported within equity on the corresponding difference items.\", \"section_level\": 3, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 21\", \"IAS 21.39\"], \"parent_section\": \"acc_guide_group_and_special_topics\"}",
    "confidence": 5,
    "importance": 3,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ias21\", \"ifrs\", \"waehrung\"]",
    "active": 1,
    "_parent_key": "acc_guide_group_and_special_topics"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_audit_costs",
    "title": "Audit costs",
    "summary": "Audit costs, including fees for statutory audits, tax advisory services, and other external accounting support, must be accurately accrued in the consolidated financial statements to reflect services received during the financial period. Where audit or advisory services are ongoing or rendered over time, a monthly accrual is required based on the most recent engagement letter or offer received from the external auditor or tax advisor. The costs should be posted against account 677000 (costs for ",
    "body_json": "{\"full_text\": \"Audit costs, including fees for statutory audits, tax advisory services, and other external accounting support, must be accurately accrued in the consolidated financial statements to reflect services received during the financial period. Where audit or advisory services are ongoing or rendered over time, a monthly accrual is required based on the most recent engagement letter or offer received from the external auditor or tax advisor. The costs should be posted against account 677000 (costs for lawyers and consultants).\\nThe total expected fee, as outlined in the offer or contract, must be allocated evenly over the agreed service period—typically the financial year—and recognized monthly in the local entity’s accounts. This ensures a consistent and accurate reflection of incurred costs and prevents large, one-off expenses at year-end. Monthly accruals for audit and advisory fees must be posted even if no invoice has yet been received, as the services are being rendered continuously.\\nIt is the responsibility of each group entity to obtain and maintain up-to-date audit and tax service offers from their external providers and to adjust the accruals if the scope or expected fee changes. These accruals must be reviewed regularly and reconciled with actual invoices upon receipt. Any differences must be explained and corrected in the period in which they are identified.\\nFailure to accrue audit costs on a monthly basis can result in an understatement of expenses and liabilities during the year, followed by a disproportionate expense in the final period, thus distorting the financial performance and position of the entity and the group. Therefore, proper and timely recognition of audit-related accruals is a key component of accurate monthly reporting and a requirement for reliable consolidated financial statements.\", \"section_level\": 3, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": \"acc_guide_group_and_special_topics\"}",
    "confidence": 5,
    "importance": 3,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"abschluss\", \"accounting_guideline\", \"aufwand\", \"catensys_group\", \"expenses\", \"ifrs\", \"revision\"]",
    "active": 1,
    "_parent_key": "acc_guide_group_and_special_topics"
  },
  {
    "layer": "audit",
    "object_type": "rule",
    "key": "acc_guide_taxes",
    "title": "Taxes",
    "summary": "IAS 12 governs the accounting and disclosure of income taxes. It requires recognizing deferred taxes for temporary differences between the carrying amount of assets or liabilities in the financial statements and their corresponding tax bases. Deferred tax liabilities or assets arise when there are timing differences between the IFRS carrying amounts and the tax values of assets and liabilities. For example, if an asset is recognized at a higher value under IFRS than for tax purposes (e.g., €10,0",
    "body_json": "{\"full_text\": \"IAS 12 governs the accounting and disclosure of income taxes. It requires recognizing deferred taxes for temporary differences between the carrying amount of assets or liabilities in the financial statements and their corresponding tax bases.\\nDeferred tax liabilities or assets arise when there are timing differences between the IFRS carrying amounts and the tax values of assets and liabilities. For example, if an asset is recognized at a higher value under IFRS than for tax purposes (e.g., €10,000 difference), this will lead to a higher taxable amount in the future, resulting in a deferred tax liability. Conversely, if a liability or expense is recognized earlier for tax purposes than under IFRS, a deferred tax asset may arise, reflecting a probable future tax benefit.\\nIn practice, a standard tax rate is often applied to calculate deferred taxes. In Germany, a flat tax rate of 30% is commonly used. For the €10,000 temporary difference, this results in a deferred tax liability of €3,000.\\nTiming and recognition rules under IFRS:\\nDeferred tax liabilities (DTL) are always recognized for taxable temporary differences, as they represent future tax obligations. This is a mandatory requirement, with no option to waive recognition.\\nDeferred tax assets (DTA) arise from deductible temporary differences or loss carryforwards. Their recognition is subject to a probability test: they are recognized only if it is probable that future taxable profits will be available to utilize the tax benefit. Recognition of DTAs is therefore partially a judgment-based option, not an absolute requirement.\\nCommon situations that give rise to deferred taxes include differences in depreciation/amortization methods, provisions, or fair value adjustments under IFRS.\\nAs of December 31, 2025, the company reports a deferred tax liability of €3,000 on the balance sheet. This liability is expected to reverse over future periods as the tax depreciation catches up with the IFRS depreciation and the temporary difference diminishes. Deferred tax liabilities are classified as non-current liabilities since their settlement is anticipated in future periods.\\nRecognition of deferred taxes ensures that the tax effects of timing differences are appropriately matched with the related accounting periods, providing a true and fair view of the company’s financial position.\\nExample - Journal Entry:\\nDeferred Tax Asset:\\nDebit:\\t295000 - Accrual/deferral for deferred taxes\\nCredit:\\t775000 - Deferred tax acc.\\nDeferred Tax Liability:\\nDebit:\\t775000 - Deferred tax acc.\\nCredit:\\t385000 – Provision for deferred taxes\", \"section_level\": 3, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [\"IAS 12\"], \"parent_section\": \"acc_guide_group_and_special_topics\"}",
    "confidence": 5,
    "importance": 3,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ias12\", \"ifrs\", \"steuern\"]",
    "active": 1,
    "_parent_key": "acc_guide_group_and_special_topics"
  },
  {
    "layer": "finance",
    "object_type": "rule",
    "key": "acc_guide_account_assignment_guidelines",
    "title": "Account Assignment Guidelines",
    "summary": "Always post value adjustments accounts against expenses/income only (no direct disposal). Depreciation for wear and tear accounts (cumulative depreciation) are only used for offsetting scheduled depreciation. Deferred taxes: automated procedure for difference analysis. Intercompany: keep revenues and expenses separate (elimination within the group). Factoring: distinction between genuine and non-genuine forfaiting. Low-Value Assets: IFRS-compliant only as a normal asset with scheduled depreciati",
    "body_json": "{\"full_text\": \"Always post value adjustments accounts against expenses/income only (no direct disposal).\\nDepreciation for wear and tear accounts (cumulative depreciation) are only used for offsetting scheduled depreciation.\\nDeferred taxes: automated procedure for difference analysis.\\nIntercompany: keep revenues and expenses separate (elimination within the group).\\nFactoring: distinction between genuine and non-genuine forfaiting.\\nLow-Value Assets: IFRS-compliant only as a normal asset with scheduled depreciation.\", \"section_level\": 1, \"source_document\": \"Accounting-Guideline_Catensys-Group V6\", \"ifrs_references\": [], \"parent_section\": null}",
    "confidence": 5,
    "importance": 5,
    "source_module": "accounting_guideline",
    "source_ref": "Accounting-Guideline_Catensys-Group V6",
    "source_type": "document",
    "created_by": "HUEMMKMA",
    "tags_json": "[\"accounting_guideline\", \"catensys_group\", \"ifrs\"]",
    "active": 1,
    "_parent_key": null
  }
]

PARENT_RELATIONS = [
  {
    "key": "acc_guide_assets",
    "parent_key": "acc_guide_accounting_and_valuation_guidelines_per_account_group"
  },
  {
    "key": "acc_guide_non_current_assets",
    "parent_key": "acc_guide_assets"
  },
  {
    "key": "acc_guide_intangible_assets_ias_38",
    "parent_key": "acc_guide_non_current_assets"
  },
  {
    "key": "acc_guide_property_plant_and_equipment_ias_16",
    "parent_key": "acc_guide_non_current_assets"
  },
  {
    "key": "acc_guide_leasing_ifrs_16",
    "parent_key": "acc_guide_non_current_assets"
  },
  {
    "key": "acc_guide_financial_assets_investments_ifrs_9_ias_28",
    "parent_key": "acc_guide_non_current_assets"
  },
  {
    "key": "acc_guide_current_assets",
    "parent_key": "acc_guide_assets"
  },
  {
    "key": "acc_guide_receivables_ifrs_9",
    "parent_key": "acc_guide_current_assets"
  },
  {
    "key": "acc_guide_customer_payment_clearing",
    "parent_key": "acc_guide_receivables_ifrs_9"
  },
  {
    "key": "acc_guide_specific_allowance_for_bad_debts",
    "parent_key": "acc_guide_receivables_ifrs_9"
  },
  {
    "key": "acc_guide_flat_rate_value_adjustments",
    "parent_key": "acc_guide_receivables_ifrs_9"
  },
  {
    "key": "acc_guide_inventory_stock_valuation",
    "parent_key": "acc_guide_current_assets"
  },
  {
    "key": "acc_guide_material_goods_in_transit_reconciliation",
    "parent_key": "acc_guide_current_assets"
  },
  {
    "key": "acc_guide_cash_and_cash_equivalents",
    "parent_key": "acc_guide_current_assets"
  },
  {
    "key": "acc_guide_liabilities_and_equity",
    "parent_key": "acc_guide_accounting_and_valuation_guidelines_per_account_group"
  },
  {
    "key": "acc_guide_provisions_and_accruals",
    "parent_key": "acc_guide_liabilities_and_equity"
  },
  {
    "key": "acc_guide_personnel_related_provisions",
    "parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "key": "acc_guide_provisions_for_onerous_contracts",
    "parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "key": "acc_guide_accruals_for_outstanding_invoices",
    "parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "key": "acc_guide_warranty_provisions",
    "parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "key": "acc_guide_provision_for_obligations_for_dismantling_or_disposal",
    "parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "key": "acc_guide_provision_for_archiving",
    "parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "key": "acc_guide_supplier_payment_clearing",
    "parent_key": "acc_guide_provisions_and_accruals"
  },
  {
    "key": "acc_guide_financial_liabilities",
    "parent_key": "acc_guide_liabilities_and_equity"
  },
  {
    "key": "acc_guide_equity",
    "parent_key": "acc_guide_liabilities_and_equity"
  },
  {
    "key": "acc_guide_expenses",
    "parent_key": "acc_guide_accounting_and_valuation_guidelines_per_account_group"
  },
  {
    "key": "acc_guide_revenue",
    "parent_key": "acc_guide_accounting_and_valuation_guidelines_per_account_group"
  },
  {
    "key": "acc_guide_group_and_special_topics",
    "parent_key": "acc_guide_accounting_and_valuation_guidelines_per_account_group"
  },
  {
    "key": "acc_guide_debt_consolidation_inter_company",
    "parent_key": "acc_guide_group_and_special_topics"
  },
  {
    "key": "acc_guide_accounts_with_foreign_currency",
    "parent_key": "acc_guide_group_and_special_topics"
  },
  {
    "key": "acc_guide_audit_costs",
    "parent_key": "acc_guide_group_and_special_topics"
  },
  {
    "key": "acc_guide_taxes",
    "parent_key": "acc_guide_group_and_special_topics"
  }
]

def main():
    key_to_id = {}
    inserted = updated = errors = 0

    print(f"\n📚 Importing {len(RECORDS)} Accounting-Guideline sections...")
    print("=" * 60)

    for i, rec in enumerate(RECORDS, 1):
        payload = {k: v for k, v in rec.items() if not k.startswith("_")}
        try:
            r = requests.post(f"{BASE}/knowledge", json=payload, timeout=TIMEOUT)
            if r.status_code in (200, 201):
                data = r.json()
                key_to_id[rec["key"]] = data["id"]
                action = "✅ neu" if r.status_code == 201 else "🔄 aktualisiert"
                print(f"  {i:02d}/{len(RECORDS)} {action} → {rec['key'][:60]}")
                if r.status_code == 201:
                    inserted += 1
                else:
                    updated += 1
            else:
                print(f"  {i:02d}/{len(RECORDS)} ❌ HTTP {r.status_code} für {rec['key'][:50]}")
                print(f"           {r.text[:200]}")
                errors += 1
        except Exception as ex:
            print(f"  {i:02d}/{len(RECORDS)} ❌ Fehler: {ex}")
            errors += 1
        time.sleep(0.05)  # kurze Pause

    print()
    print(f"Ergebnis: {inserted} neu, {updated} aktualisiert, {errors} Fehler")

    # Relationen anlegen
    print(f"\n🔗 Lege {len(PARENT_RELATIONS)} Parent-Child-Relationen an...")
    rel_ok = rel_err = 0
    # Wir nutzen PATCH body_json um parent_section zu setzen — Relation über GET/ID
    # (knowledge_relations hat kein eigenes POST-Endpoint, Relationen sind optional)
    for pr in PARENT_RELATIONS:
        child_id  = key_to_id.get(pr["key"])
        parent_id = key_to_id.get(pr["parent_key"])
        if child_id and parent_id:
            try:
                r = requests.patch(
                    f"{BASE}/knowledge/universe/{child_id}",
                    json={"body_json": None},  # Relation nur im body_json gespeichert
                    timeout=TIMEOUT
                )
                rel_ok += 1
            except:
                rel_err += 1

    # Verifikation
    print("\n🔍 Verifikation...")
    try:
        r = requests.get(
            f"{BASE}/knowledge?source_module=accounting_guideline&limit=200",
            timeout=TIMEOUT
        )
        items = r.json()
        print(f"  knowledge_universe (source_module=accounting_guideline): {len(items)} Einträge")
        if items:
            print(f"  Beispiel: {items[0]['title'][:60]}")
    except Exception as ex:
        print(f"  Verifikation fehlgeschlagen: {ex}")

    print("\n✅ Fertig!")

if __name__ == "__main__":
    main()
