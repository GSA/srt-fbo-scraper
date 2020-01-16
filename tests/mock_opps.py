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



mock_opp_one = {'opp_id': 'test', 'title': 'Vacuum whole plugs', 'solicitationNumber': 'SPMYM3-20-Q-7009', 'agency': 'agency', 'subTier': 'DEFENSE LOGISTICS AGENCY (DLA)', 'office': 'office', 'postedDate': '2019-12-18', 'type': 'Combined Synopsis/Solicitation', 'baseType': 'Combined Synopsis/Solicitation', 'archiveType': 'autocustom', 'archiveDate': '2020-12-25', 'typeOfSetAsideDescription': None, 'setaside': 'test', 'responseDeadLine': '2019-12-31T15:00:00-05:00', 'naics': 'test', 'classificationCode': '5330', 'active': 'Yes', 'award': None, 'pointOfContact': [{'fax': '2074382451', 'type': 'primary', 'email': 'donna.j.quill@navy.mil', 'phone': '2074382386', 'title': None, 'fullName': 'Donna Quill'}], 'description': 'https://api.sam.gov/prod/opportunities/v1/noticedesc?noticeid=fe4d65bed0b2472b8fc1cb63340ea4aa', 'organizationType': 'OFFICE', 'officeAddress': {'zipcode': '03801-5000', 'city': 'PORTSMOUTH', 'countryCode': 'USA', 'state': 'NH'}, 'placeOfPerformance': {'city': {'code': '37270', 'name': 'Kittery'}, 'state': {'code': 'ME', 'name': 'Maine'}, 'zip': '03904', 'country': {'code': 'USA', 'name': 'UNITED STATES'}}, 'additionalInfoLink': None, 'uiLink': 'https://beta.sam.gov/opp/fe4d65bed0b2472b8fc1cb63340ea4aa/view', 'links': [{'rel': 'self', 'href': 'https://api.sam.gov/prod/opportunities/v1/search?noticeid=fe4d65bed0b2472b8fc1cb63340ea4aa&limit=1', 'hreflang': None, 'media': None, 'title': None, 'type': None, 'deprecation': None}]}

mock_opp_two = {'opp_id': 'test', 'title': 'Combined Synopsis/Solicitation PSE for EA-18G', 'solicitationNumber': 'N68335-20-Q-0059', 'agency': 'agency', 'subTier': 'DEPT OF THE NAVY', 'office': 'office', 'postedDate': '2019-12-18', 'type': 'Combined Synopsis/Solicitation', 'baseType': 'Combined Synopsis/Solicitation', 'archiveType': 'auto15', 'archiveDate': '2020-01-18', 'typeOfSetAsideDescription': None, 'setaside': 'test', 'responseDeadLine': '2020-01-03T12:00:00-05:00', 'naics': 'test', 'classificationCode': '5120', 'active': 'Yes', 'award': None, 'pointOfContact': [{'fax': '7323232359', 'type': 'primary', 'email': 'desiree.pendleton@navy.mil', 'phone': '732-323-2155', 'title': None, 'fullName': 'Desiree Pendleton'}], 'description': 'https://api.sam.gov/prod/opportunities/v1/noticedesc?noticeid=fc0371c2a20c4eaa8bf70976bf27a83b', 'organizationType': 'OFFICE', 'officeAddress': {'zipcode': '08733', 'city': 'JOINT BASE MDL', 'countryCode': 'USA', 'state': 'NJ'}, 'placeOfPerformance': {'country': {'code': 'USA', 'name': 'UNITED STATES'}}, 'additionalInfoLink': None, 'uiLink': 'https://beta.sam.gov/opp/fc0371c2a20c4eaa8bf70976bf27a83b/view', 'links': [{'rel': 'self', 'href': 'https://api.sam.gov/prod/opportunities/v1/search?noticeid=fc0371c2a20c4eaa8bf70976bf27a83b&limit=1', 'hreflang': None, 'media': None, 'title': None, 'type': None, 'deprecation': None}]}


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

mock_opps = [mock_opp_one, mock_opp_two]

#mock_data = {'_embedded': {'results': mock_opps}}

mock_data = {'opportunitiesData': mock_opps}

mock_schematized_opp_one = {'notice type': 'test', 'solnbr': 'test', 'agency': 'agency', 'compliant': 0, 'office': 'office', 'opp_id': 'test', 'attachments': [], 'classcod': 'test', 'naics': 'test', 'subject': 'test', 'url': 'https://beta.sam.gov/opp/123/view', 'setaside': 'test', 'emails': ['test@test.gov']}

mock_attachment_data = {'text': 'test', 'filename': 'test.txt', 'machine_readable': True, 'url': 'test', 'prediction': None, 'decision_boundary': None, 'validation': None, 'trained': False}

mock_transformed_opp_one = {'notice type': 'test', 'solnbr': 'test', 'agency': 'agency', 'compliant': 0, 'office': 'office', 'attachments': [mock_attachment_data], 'classcod': 'test', 'naics': 'test', 'subject': 'test', 'url': 'https://beta.sam.gov/opp/123/view', 'setaside': 'test', 'emails': ['test@test.gov']}

mock_data_for_db = {'notice type': 'Presolicitation', 'solnbr': 'test', 'agency': 'agency', 'compliant': 0, 'office': 'office', 'attachments': [mock_attachment_data], 'classcod': 'test', 'naics': 'test', 'subject': 'test', 'url': 'url', 'setaside': 'test', 'emails': ['test@test.gov']}