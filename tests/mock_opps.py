#mock_opp_one = {'data': {'link': {'href': 'test.com',
#   'additionalInfo': {'content': 'description'}},
#  'type': 'p',
#  'award': {'awardee': {'location': {}},
#   'fairOpportunity': {},
#   'justificationAuthority': {}},
#  'naics': [{'code': ['123'], 'type': 'primary'}],
#  'title': 'test',
#  'archive': {'date': '2019-10-09', 'type': 'autocustom'},
#  'permissions': {'IVL': {'read': False,
#    'create': False,
#    'delete': False,
#    'update': False}},
#  'descriptions': [],
#  'solicitation': {'deadlines': {'response': '2019-10-08T23:59:59-04:00',
#    'responseTz': 'America/New_York'}},
#  'organizationId': '100176853',
#  'pointOfContact': [{'type': 'primary',
#    'email': 'test@test.gov',
#    'fullName': 'Name',
#    'additionalInfo': {'content': 'Description mail'}}],
#  'classificationCode': 'test',
#  'placeOfPerformance': {'zip': '20170',
#   'country': {'code': 'USA', 'name': 'UNITED STATES'},
#   'streetAddress': 'Alton Sq'},
#  'solicitationNumber': 'test',
#  'additionalReporting': ['none'],
#  'organizationLocationId': '50175943'},
# 'additionalInfo': {'sections': [{'id': 'header', 'status': 'updated'},
#   {'id': 'award', 'status': 'updated'},
#   {'id': 'general', 'status': 'updated'},
#   {'id': 'classification', 'status': 'updated'},
#   {'id': 'description', 'status': 'updated'},
#   {'id': 'attachments-links', 'status': 'updated'},
#   {'id': 'contact', 'status': 'updated'}]},
# 'parent': {},
# 'related': {},
# 'status': {'code': 'published', 'value': 'Published'},
# 'archived': False,
# 'cancelled': False,
# 'latest': True,
# 'deleted': False,
# 'postedDate': '2019-09-25T21:43:03.675+0000',
# 'modifiedDate': 'modDate',
# 'createdDate': '2019-09-25T21:42:23.210+0000',
# 'modifiedBy': '',
# 'createdBy': '',
# 'opportunityId': 'test'}
#
#mock_opp_two = {'data': {'link': {'href': 'testy.com',
#   'additionalInfo': {'content': 'description'}},
#  'type': 'p',
#  'award': {'awardee': {'location': {}},
#   'fairOpportunity': {},
#   'justificationAuthority': {}},
#  'naics': [{'code': ['123'], 'type': 'primary'}],
#  'title': 'testy',
#  'archive': {'date': '2019-10-09', 'type': 'autocustom'},
#  'permissions': {'IVL': {'read': False,
#    'create': False,
#    'delete': False,
#    'update': False}},
#  'descriptions': [],
#  'solicitation': {'deadlines': {'response': '2019-10-08T23:59:59-04:00',
#    'responseTz': 'America/New_York'}},
#  'organizationId': '100176853',
#  'pointOfContact': [{'type': 'primary',
#    'email': 'testy@testy.gov',
#    'fullName': 'Name',
#    'additionalInfo': {'content': 'Description mail'}}],
#  'classificationCode': 'testy',
#  'placeOfPerformance': {'zip': '20170',
#   'country': {'code': 'USA', 'name': 'UNITED STATES'},
#   'streetAddress': 'Alton Sq'},
#  'solicitationNumber': 'testy',
#  'additionalReporting': ['none'],
#  'organizationLocationId': '50175943'},
# 'additionalInfo': {'sections': [{'id': 'header', 'status': 'updated'},
#   {'id': 'award', 'status': 'updated'},
#   {'id': 'general', 'status': 'updated'},
#   {'id': 'classification', 'status': 'updated'},
#   {'id': 'description', 'status': 'updated'},
#   {'id': 'attachments-links', 'status': 'updated'},
#   {'id': 'contact', 'status': 'updated'}]},
# 'parent': {},
# 'related': {},
# 'status': {'code': 'published', 'value': 'Published'},
# 'archived': False,
# 'cancelled': False,
# 'latest': True,
# 'deleted': False,
# 'postedDate': '2019-09-25T21:43:03.675+0000',
# 'modifiedDate': 'modDate',
# 'createdDate': '2019-09-25T21:42:23.210+0000',
# 'modifiedBy': '',
# 'createdBy': '',
# 'opportunityId': 'testy'}
#

mock_opp_one = [
    {'psc': [
        {'code': 'U012', 'id': 5029, 'value': 'INFORMATION TRAINING'},
        {'code': 'U0', 'id': 5006, 'value': 'EDUCATION AND TRAINING SERVICES'}],
        'isCanceled': False,
        'solicitation': {
            'originalSetAside': None,
            'setAside': {'code': 'SBA', 'value': 'Total Small Business Set-Aside (FAR 19.5)'}
        },
        'suggestion': {'input': ['27 inch monitors', 'fy19-12306', 'fy1912306'],
                       'contexts': {'isActive': True}},
        '_rScore': 0,
        'pointOfContacts': [{'phone': '8052280442', 'fullName': 'RACHEL T. SMITH', 'fax': '8052285718', 'type': 'primary', 'title': 'Contract Specialist', 'email': 'RACHEL.T.SMITH@NAVY.MIL'}],
        'publishDate': '2019-12-13T15:30:48-05:00',
        'indexedDate': '2019-12-26T00:01:52-05:00',
        'type': {'code': 'a', 'value': 'Award Notice'},
        'title': '27 Inch Monitors',
        'isActive': False,
        'placeOfPerformance': [
        {'zip': '93043', 'city': '58296', 'streetAddress': None, 'streetAddress2': None, 'state': 'CA'}],
        'solicitationNumber': 'FY19-12306', 'additionalReporting': ['none'],
        'award': {'date': '2019-12-10', 'number': 'N6339420P0004', 'amount': 391977.02,
                  'awardee': {'name': 'MILLI MICRO SYSTEMS, INC.', 'duns': '033273660',
                              'location': {'zip': None, 'country': 'USA', 'city': '52176',
                                           'streetAddress': None, 'streetAddress2': None, 'state': 'CA'}},
                  'justificationAuthority': {'authority': {'code': None, 'value': None},
                                             'modificationNumber': None},
                  'additionalInfo': 'MILLI MICRO SYSTEMS, INC.', 'deliveryOrderNumber': None,
                  'fairOpportunity': {'authority': {'code': None, 'value': None}}},
        'cleanSolicitationNumber': 'FY1912306', 'archiveDate': '2019-12-25T00:00:00-05:00',
        'modifiedDate': '2019-12-25T23:56:37-05:00', 'organizationHierarchy': [{'organizationId': '100000000',
                                                                                'address': {'zip': None,
                                                                                            'country': None,
                                                                                            'city': None,
                                                                                            'streetAddress': None,
                                                                                            'streetAddress2': None,
                                                                                            'state': None},
                                                                                'level': 1,
                                                                                'name': 'DEPARTMENT OF DEFENSE',
                                                                                'type': 'DEPARTMENT',
                                                                                'status': 'active'},
                                                                               {'organizationId': '300000188',
                                                                                'address': {'zip': None,
                                                                                            'country': None,
                                                                                            'city': None,
                                                                                            'streetAddress': None,
                                                                                            'streetAddress2': None,
                                                                                            'state': None},
                                                                                'level': 2,
                                                                                'name': 'DEPT OF THE NAVY',
                                                                                'type': 'AGENCY',
                                                                                'status': 'active'},
                                                                               {'organizationId': '100005213',
                                                                                'address': {'zip': None,
                                                                                            'country': None,
                                                                                            'city': None,
                                                                                            'streetAddress': None,
                                                                                            'streetAddress2': None,
                                                                                            'state': None},
                                                                                'level': 3, 'name': 'NAVSEA',
                                                                                'type': 'MAJOR COMMAND',
                                                                                'status': 'active'},
                                                                               {'organizationId': '100076477',
                                                                                'address': {'zip': None,
                                                                                            'country': None,
                                                                                            'city': None,
                                                                                            'streetAddress': None,
                                                                                            'streetAddress2': None,
                                                                                            'state': None},
                                                                                'level': 4,
                                                                                'name': 'NAVSEA WARFARE CENTER',
                                                                                'type': 'SUB COMMAND',
                                                                                'status': 'active'},
                                                                               {'organizationId': '100076483',
                                                                                'address': {
                                                                                    'zip': '93043-5007',
                                                                                    'country': 'USA',
                                                                                    'city': 'PORT HUENEME',
                                                                                    'streetAddress': 'NAVAL SURFACE WARFARE CENTER PHD',
                                                                                    'streetAddress2': '4363 MISSILE WAY',
                                                                                    'state': 'CA'}, 'level': 5,
                                                                                'name': 'COMMANDING OFFICER',
                                                                                'type': 'OFFICE',
                                                                                'status': 'active'}],
        '_id': '532e8551391a4ba784e1e186656b6a39', 'naics': [{'code': '334118', 'id': 5433,
                                                              'value': 'Computer Terminal and Other Computer Peripheral Equipment Manufacturing'}],
        'modifications': {'count': 0}}]

mock_opp_two = [{'psc': [{'code': 'R', 'id': 4719, 'value': 'SUPPORT SVCS (PROF, ADMIN, MGMT)'}, {'code': None, 'id': None, 'value': None}], 'isCanceled': False, 'solicitation': {'originalSetAside': None, 'setAside': None}, 'publishDate': '2019-12-14T09:56:29-05:00', 'type': {'code': 'o', 'value': 'Solicitation'}, 'title': 'R--ON-SITE SHREDDING SERVICES | HRC - BALT | 392  "TIERED EVALUATIONS - FOR SMALL BUSINESS"', 'isActive': False, 'descriptions': [{'lastModifiedDate': '2019-12-14T09:56:29.749-05:00', 'content': 'The Department of Veterans Affairs, Veterans Benefits Administration, Human Resource Center, Baltimore, MD, has a 60-month requirement for on-site confidential shredding services.    \n\n The VA intends to make a single (all or none), firm-fixed price award.\nThe NAICS code applicable to this procurement is 561990 and this procurement will be set aside as  Tiered evaluations for small business concerns  in accordance with 38 U.S.C. § 8127(i).  Prospective bidders should continue to monitor https://beta.sam.gov/ where it is anticipated a solicitation containing the details of this requirement will be posted within the next seven (7) days.  (This website has officially replaced FBO.gov).  No other information about this opportunity is available at this time.'}], 'additionalReporting': ['none'], 'responseDate': '2019-12-23T23:59:59-05:00', 'award': {'date': None, 'number': None, 'amount': None, 'awardee': {'name': None, 'duns': None, 'location': {'zip': None, 'country': None, 'city': None, 'streetAddress': None, 'streetAddress2': None, 'state': None}}, 'justificationAuthority': {'authority': {'code': None, 'value': None}, 'modificationNumber': None}, 'additionalInfo': None, 'deliveryOrderNumber': None, 'fairOpportunity': {'authority': {'code': None, 'value': None}}}, 'cleanSolicitationNumber': '36C10E20Q0061', 'archiveDate': '2020-01-07T00:00:00-05:00', 'organizationHierarchy': [{'organizationId': '100006568', 'address': {'zip': None, 'country': 'US', 'city': None, 'streetAddress': None, 'streetAddress2': None, 'state': None}, 'level': 1, 'name': 'VETERANS AFFAIRS, DEPARTMENT OF', 'type': 'DEPARTMENT', 'status': 'active'}, {'organizationId': '300000214', 'address': {'zip': None, 'country': None, 'city': None, 'streetAddress': None, 'streetAddress2': None, 'state': None}, 'level': 2, 'name': 'VETERANS AFFAIRS, DEPARTMENT OF', 'type': 'AGENCY', 'status': 'active'}, {'organizationId': '100170296', 'address': {'zip': '20006', 'country': 'USA', 'city': 'WASHINGTON', 'streetAddress': '1800 G STREET NW', 'streetAddress2': None, 'state': 'DC'}, 'level': 3, 'name': 'VBA FIELD CONTRACTING (36C10E)', 'type': 'OFFICE', 'status': 'active'}], 'modifications': {'count': 0}, 'suggestion': {'input': ['r--on-site shredding services | hrc - balt | 392  "tiered evaluations - for small business"  ', '36c10e20q0061', '36c10e20q0061'], 'contexts': {'isActive': True}}, '_rScore': 0, 'pointOfContacts': [{'additionalInfo': {'content': 'kimberly.tomasi@va.gov'}, 'fullName': 'Kimberly M Tomasi\nContract Specialist\n401-223-3777', 'type': 'primary', 'email': 'kimberly.tomasi@va.gov'}], '_type': 'opportunity', 'indexedDate': '2020-01-08T00:01:55-05:00', 'placeOfPerformance': [{'zip': None, 'city': None, 'streetAddress': None, 'streetAddress2': None, 'state': None}], 'solicitationNumber': '36C10E20Q0061', 'modifiedDate': '2020-01-07T23:55:40-05:00', '_id': '998f586f5e1d4237bafaac483c5d9966', 'naics': [{'code': '561990', 'id': 1921, 'value': 'All Other Support Services'}]}]

mock_opps = [mock_opp_one[0], mock_opp_two[0]]

mock_data = {'_embedded': {'results': mock_opps}}

mock_schematized_opp_one = {'notice type': 'test', 'solnbr': 'test', 'agency': 'agency', 'compliant': 0, 'office': 'office', 'opp_id': 'test', 'attachments': [], 'classcod': 'test', 'naics': 'test', 'subject': 'test', 'url': 'https://beta.sam.gov/opp/123/view', 'setaside': 'test', 'emails': ['test@test.gov']}

mock_attachment_data = {'text': 'test', 'filename': 'test.txt', 'machine_readable': True, 'url': 'test', 'prediction': None, 'decision_boundary': None, 'validation': None, 'trained': False}

mock_bad_attachment_data = {'text': 'This notice contains link(s). To view, enter the below URLs in your web browser:\n\n -    https://www.dibbs.bsm.dla.mil/rfq/rfqrec.aspx?sn=SPE4A620T402G', 'filename': 'test.txt', 'machine_readable': True, 'url': 'test', 'prediction': None, 'decision_boundary': None, 'validation': None, 'trained': False}

mock_transformed_opp_one = {'notice type': 'test', 'solnbr': 'test', 'agency': 'agency', 'compliant': 0, 'office': 'office', 'attachments': [mock_attachment_data], 'classcod': 'test', 'naics': 'test', 'subject': 'test', 'url': 'https://beta.sam.gov/opp/123/view', 'setaside': 'test', 'emails': ['test@test.gov']}

mock_transformed_opp_bad_attachment = {'notice type': 'test', 'solnbr': 'test', 'agency': 'agency', 'compliant': 0, 'office': 'office', 'attachments': [mock_bad_attachment_data], 'classcod': 'test', 'naics': 'test', 'subject': 'test', 'url': 'https://beta.sam.gov/opp/123/view', 'setaside': 'test', 'emails': ['test@test.gov']}

mock_data_for_db = {'notice type': 'Presolicitation', 'solnbr': 'test', 'agency': 'agency', 'compliant': 0, 'office': 'office', 'attachments': [mock_attachment_data], 'classcod': 'test', 'naics': 'test', 'subject': 'test', 'url': 'url', 'setaside': 'test', 'emails': ['test@test.gov']}