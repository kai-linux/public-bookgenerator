from flask import Blueprint, jsonify, request, send_file, Response
from flask_cors import cross_origin
import os
import uuid
import threading
import time
import json
from datetime import datetime
import io
import zipfile

book_bp = Blueprint('book', __name__)

# In-memory storage for generation status (in production, use Redis or database)
generation_status = {}
generated_files = {}

def create_simple_docx(title, author, chapters_data):
    """Create a simple DOCX file using basic XML structure"""
    
    # DOCX is essentially a ZIP file with XML content
    docx_buffer = io.BytesIO()
    
    with zipfile.ZipFile(docx_buffer, 'w', zipfile.ZIP_DEFLATED) as docx:
        # Add [Content_Types].xml
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''
        docx.writestr('[Content_Types].xml', content_types)
        
        # Add _rels/.rels
        rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
        docx.writestr('_rels/.rels', rels)
        
        # Create document content
        document_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p>
            <w:pPr>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:sz w:val="48"/>
                    <w:b/>
                </w:rPr>
                <w:t>{title}</w:t>
            </w:r>
        </w:p>'''
        
        if author:
            document_content += f'''
        <w:p>
            <w:pPr>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:sz w:val="24"/>
                </w:rPr>
                <w:t>By: {author}</w:t>
            </w:r>
        </w:p>'''
        
        # Add page break
        document_content += '''
        <w:p>
            <w:r>
                <w:br w:type="page"/>
            </w:r>
        </w:p>'''
        
        # Add chapters
        for chapter_num, chapter_content in chapters_data:
            document_content += f'''
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:sz w:val="32"/>
                    <w:b/>
                </w:rPr>
                <w:t>Chapter {chapter_num}</w:t>
            </w:r>
        </w:p>'''
            
            for paragraph in chapter_content:
                document_content += f'''
        <w:p>
            <w:r>
                <w:t>{paragraph}</w:t>
            </w:r>
        </w:p>'''
        
        document_content += '''
    </w:body>
</w:document>'''
        
        docx.writestr('word/document.xml', document_content)
    
    docx_buffer.seek(0)
    return docx_buffer

def simulate_book_generation(job_id, book_config):
    """Simulate AI book generation process"""
    try:
        # Update status to processing
        generation_status[job_id] = {
            'status': 'processing',
            'progress': 0,
            'message': 'Starting book generation...',
            'created_at': datetime.now().isoformat()
        }
        
        # Simulate generation steps
        steps = [
            (10, 'Analyzing book configuration...'),
            (25, 'Generating book outline...'),
            (40, 'Creating chapter content...'),
            (60, 'Writing introduction and conclusion...'),
            (80, 'Formatting document...'),
            (95, 'Finalizing book structure...'),
            (100, 'Book generation complete!')
        ]
        
        for progress, message in steps:
            time.sleep(2)  # Simulate processing time
            generation_status[job_id].update({
                'progress': progress,
                'message': message
            })
        
        # Generate actual content
        num_chapters = book_config.get('chapters', 5)
        genre = book_config.get('genre', 'General')
        length = book_config.get('length', 'medium')
        title = book_config.get('title', 'Generated Book')
        author = book_config.get('author', '')
        
        chapters_data = []
        
        for i in range(1, num_chapters + 1):
            # Generate sample content based on genre and length
            if length == 'short':
                paragraphs = 2
            elif length == 'long':
                paragraphs = 6
            else:  # medium
                paragraphs = 4
            
            chapter_content = []
            for j in range(paragraphs):
                if genre.lower() == 'fiction':
                    content = f"This is a fictional narrative for Chapter {i}, paragraph {j+1}. The story unfolds with compelling characters and an engaging plot that keeps readers interested throughout the chapter."
                elif genre.lower() == 'non-fiction':
                    content = f"This chapter covers important factual information and insights. Paragraph {j+1} provides detailed analysis and evidence-based content that educates and informs the reader."
                elif genre.lower() == 'mystery':
                    content = f"The mystery deepens in Chapter {i}. Clues emerge in paragraph {j+1} that will help solve the puzzle, but new questions arise that keep the reader guessing."
                else:
                    content = f"Chapter {i}, paragraph {j+1} contains engaging content tailored to the {genre} genre, providing valuable information and entertainment for the reader."
                
                chapter_content.append(content)
            
            chapters_data.append((i, chapter_content))
        
        # Create DOCX file
        docx_buffer = create_simple_docx(title, author, chapters_data)
        
        # Save the document
        filename = f"book_{job_id}.docx"
        filepath = os.path.join('/tmp', filename)
        
        with open(filepath, 'wb') as f:
            f.write(docx_buffer.getvalue())
        
        # Store file info
        generated_files[job_id] = {
            'filename': filename,
            'filepath': filepath,
            'created_at': datetime.now().isoformat()
        }
        
        # Update final status
        generation_status[job_id].update({
            'status': 'completed',
            'progress': 100,
            'message': 'Book generation complete!',
            'file_ready': True
        })
        
    except Exception as e:
        generation_status[job_id] = {
            'status': 'error',
            'progress': 0,
            'message': f'Error generating book: {str(e)}',
            'created_at': datetime.now().isoformat()
        }

@book_bp.route('/generate', methods=['POST'])
@cross_origin()
def generate_book():
    """Start book generation process"""
    try:
        data = request.json
        
        # Validate required fields
        if not data or not data.get('title'):
            return jsonify({'error': 'Book title is required'}), 400
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize status
        generation_status[job_id] = {
            'status': 'queued',
            'progress': 0,
            'message': 'Book generation queued...',
            'created_at': datetime.now().isoformat()
        }
        
        # Start generation in background thread
        thread = threading.Thread(target=simulate_book_generation, args=(job_id, data))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'message': 'Book generation started'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@book_bp.route('/status/<job_id>', methods=['GET'])
@cross_origin()
def get_generation_status(job_id):
    """Get generation status for a job"""
    if job_id not in generation_status:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(generation_status[job_id])

@book_bp.route('/download/<job_id>', methods=['GET'])
@cross_origin()
def download_book(job_id):
    """Download generated book"""
    if job_id not in generated_files:
        return jsonify({'error': 'File not found'}), 404
    
    file_info = generated_files[job_id]
    filepath = file_info['filepath']
    filename = file_info['filename']
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File no longer exists'}), 404
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

@book_bp.route('/jobs', methods=['GET'])
@cross_origin()
def list_jobs():
    """List all generation jobs"""
    return jsonify(generation_status)

