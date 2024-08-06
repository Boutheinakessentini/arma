# views.py
import xml.etree.ElementTree as ET
from django.shortcuts import render
from .forms import XMLUploadForm

def upload_xml(request):
    if request.method == 'POST':
        form = XMLUploadForm(request.POST, request.FILES)
        if form.is_valid():
            xml_file = request.FILES['xml_file']
            file_content = xml_file.read().decode('utf-8')
            
            root = ET.fromstring(file_content)
            
            def parse_element(element):
                parsed = {}
                for child in element:
                    if child.tag == 'parameter':
                        parsed[child.find('./name').text] = {
                            'id': child.find('./id').text,
                            'description': child.find('./description').text or None,
                            'value': child.find('./value').text,
                            'type': child.find('./value').get('type'),
                        }
                    elif child.tag == 'measure':
                        parsed[child.get('step')] = {
                            'config': child.find('./config').text,
                            'value': child.find('./value').text,
                            'failed': child.find('./failed').text,
                            'duration': child.find('./duration').text,
                            'unit': child.find('./unit').text,
                            'used': child.find('./used').text,
                            'limit': {
                                'id': child.find('./limit').get('id'),
                                'name': child.find('./limit').get('name'),
                                'value1': child.find('./limit/value1').text,
                                'value2': child.find('./limit/value2').text,
                            }
                        }
                    elif child.tag in ('product', 'global', 'init', 'cleanup', 'version'):
                        parsed[child.tag] = {
                            k: v.text or None for k, v in child.items()
                        }
                        for sub_child in child:
                            parsed[child.tag][sub_child.tag] = sub_child.text or None
                    elif child.tag == 'process':
                        parsed[child.get('stage')] = {
                            'name': child.find('./name').text,
                            'description': child.find('./description').text or None,
                            'init': {
                                'failed': child.find('./init/failed').text,
                                'duration': child.find('./init/duration').text or None,
                            },
                            'test': {},
                            'cleanup': {
                                'failed': child.find('./cleanup/failed').text,
                                'duration': child.find('./cleanup/duration').text or None,
                            }
                        }
                        for test in child.findall('test'):
                            parsed[child.get('stage')]['test'][test.get('step')] = {
                                'id': test.find('./id').text,
                                'name': test.find('./name').text,
                                'description': test.find('./description').text,
                                'failed': test.find('./failed').text,
                                'duration': test.find('./duration').text or None,
                                'used': test.find('./used').text,
                                'parameter': parse_element(test.find('./parameter')) if test.find('./parameter') is not None else None,
                                'measure': parse_element(test.find('./measure')) if test.find('./measure') is not None else None,
                            }
                    elif len(child) > 0:
                        parsed[child.tag] = parse_element(child)
                    else:
                        parsed[child.tag] = child.text
                return parsed

            xml_data = parse_element(root)
            
            context = {
                'xml_data': xml_data,
                'raw_xml': file_content,  # Include raw XML if needed
            }
            return render(request, 'analyzer/display_xml.html', context)
    else:
        form = XMLUploadForm()
    
    context = {'form': form}
    return render(request, 'analyzer/upload.html', context)
