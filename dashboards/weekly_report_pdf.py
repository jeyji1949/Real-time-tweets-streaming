#!/usr/bin/env python3
"""
Génère un rapport hebdomadaire en PDF
"""

from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
import matplotlib.pyplot as plt
import io

class WeeklyPDFReport:
    def __init__(self):
        self.es = Elasticsearch(["http://localhost:9200"])
    
    def get_week_stats(self):
        """Stats de la semaine passée"""
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        query = {
            "query": {
                "range": {
                    "created_at": {
                        "gte": week_ago.isoformat(),
                        "lte": today.isoformat()
                    }
                }
            },
            "aggs": {
                "by_day": {
                    "date_histogram": {
                        "field": "created_at",
                        "calendar_interval": "day"
                    },
                    "aggs": {
                        "by_sentiment": {
                            "terms": {"field": "sentiment.keyword"}
                        }
                    }
                },
                "by_sentiment": {
                    "terms": {"field": "sentiment.keyword"}
                },
                "by_topic": {
                    "terms": {"field": "topic.keyword", "size": 10}
                },
                "top_users": {
                    "terms": {"field": "user.keyword", "size": 10}
                },
                "total_engagement": {
                    "sum": {"field": "like_count"}
                }
            },
            "size": 0
        }
        
        result = self.es.search(index="tweets_index_improved", body=query)
        
        return result
    
    def create_sentiment_chart(self, data):
        """Crée un graphique en camembert"""
        sentiments = {
            bucket['key']: bucket['doc_count'] 
            for bucket in data['aggregations']['by_sentiment']['buckets']
        }
        
        fig, ax = plt.subplots(figsize=(6, 4))
        colors_map = {
            'positive': '#52C41A',
            'neutral': '#8C8C8C',
            'negative': '#F5222D'
        }
        
        labels = list(sentiments.keys())
        sizes = list(sentiments.values())
        colors_list = [colors_map.get(label, '#1890FF') for label in labels]
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors_list, startangle=90)
        ax.axis('equal')
        
        # Sauvegarder dans un buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return buf
    
    def create_timeline_chart(self, data):
        """Crée un graphique de timeline"""
        daily_data = data['aggregations']['by_day']['buckets']
        
        dates = [datetime.fromisoformat(bucket['key_as_string'].replace('Z', ''))
                 for bucket in daily_data]
        counts = [bucket['doc_count'] for bucket in daily_data]
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(dates, counts, marker='o', color='#1890FF', linewidth=2)
        ax.set_xlabel('Date')
        ax.set_ylabel('Nombre de tweets')
        ax.set_title('Évolution quotidienne')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return buf
    
    def generate_pdf(self, filename=None):
        """Génère le PDF"""
        if filename is None:
            filename = f"rapport_hebdo_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1890FF'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        title = Paragraph(
            f"Rapport Hebdomadaire<br/>Analyse Twitter<br/>{datetime.now().strftime('%d/%m/%Y')}",
            title_style
        )
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Récupérer les stats
        data = self.get_week_stats()
        total = data['hits']['total']['value']
        
        # Résumé exécutif
        summary_style = styles['Heading2']
        story.append(Paragraph("📊 Résumé Exécutif", summary_style))
        story.append(Spacer(1, 0.2*inch))
        
        summary_text = f"""
        <b>Total de tweets cette semaine :</b> {total}<br/>
        <b>Période :</b> {(datetime.now() - timedelta(days=7)).strftime('%d/%m/%Y')} - {datetime.now().strftime('%d/%m/%Y')}<br/>
        <b>Engagement total (likes) :</b> {int(data['aggregations']['total_engagement']['value'])}
        """
        
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Graphique sentiment
        story.append(Paragraph("😊 Distribution des Sentiments", summary_style))
        story.append(Spacer(1, 0.2*inch))
        
        chart_buf = self.create_sentiment_chart(data)
        img = Image(chart_buf, width=4*inch, height=3*inch)
        story.append(img)
        story.append(Spacer(1, 0.3*inch))
        
        # Timeline
        story.append(Paragraph("📈 Évolution Quotidienne", summary_style))
        story.append(Spacer(1, 0.2*inch))
        
        timeline_buf = self.create_timeline_chart(data)
        img2 = Image(timeline_buf, width=5*inch, height=3*inch)
        story.append(img2)
        story.append(Spacer(1, 0.3*inch))
        
        # Top Topics
        story.append(Paragraph("🎯 Top 5 Topics", summary_style))
        story.append(Spacer(1, 0.2*inch))
        
        topics_data = [['Rang', 'Topic', 'Nombre de tweets']]
        for i, bucket in enumerate(data['aggregations']['by_topic']['buckets'][:5], 1):
            topics_data.append([str(i), bucket['key'], str(bucket['doc_count'])])
        
        topics_table = Table(topics_data, colWidths=[1*inch, 2*inch, 2*inch])
        topics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(topics_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Top Users
        story.append(Paragraph("👥 Top 5 Contributeurs", summary_style))
        story.append(Spacer(1, 0.2*inch))
        
        users_data = [['Rang', 'Utilisateur', 'Nombre de tweets']]
        for i, bucket in enumerate(data['aggregations']['top_users']['buckets'][:5], 1):
            users_data.append([str(i), bucket['key'], str(bucket['doc_count'])])
        
        users_table = Table(users_data, colWidths=[1*inch, 2*inch, 2*inch])
        users_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#52C41A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(users_table)
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer = Paragraph(
            "<i>Rapport généré automatiquement par Twitter Analytics Pipeline</i>",
            styles['Normal']
        )
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        print(f"✅ Rapport PDF sauvegardé : {filename}")
        
        return filename


if __name__ == "__main__":
    generator = WeeklyPDFReport()
    generator.generate_pdf()