import sqlite3
import json
from typing import List, Dict
from datetime import datetime
from arxiv import Search, SortCriterion

class ResearchDatabase:
    def __init__(self, db_file="papers.db"):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                title TEXT,
                authors TEXT,
                summary TEXT,
                published_date TEXT,
                topic TEXT,
                analysis TEXT
            )
        """)
        
        cursor.execute("PRAGMA table_info(papers);")
        columns = cursor.fetchall()
        
        column_names = [column[1] for column in columns]
        if 'topic' not in column_names:
            cursor.execute("ALTER TABLE papers ADD COLUMN topic TEXT;")
            self.conn.commit()
        
        self.conn.commit()

    def add_paper(self, id: str, title: str, authors: List[str], summary: str, published_date: str, topic: str, analysis: str = ''):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO papers (id, title, authors, summary, published_date, topic, analysis) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id, title, json.dumps(authors), summary, published_date, topic, analysis))
        self.conn.commit()

    def get_papers_by_topic(self, topic: str, limit: int = 10) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM papers WHERE topic LIKE ? ORDER BY published_date DESC LIMIT ?
        """, (f"%{topic}%", limit))
        papers = cursor.fetchall()
        if not papers:
            return []
        return [{"id": paper[0], "title": paper[1], "authors": json.loads(paper[2]), "summary": paper[3], "published_date": paper[4], "topic": paper[5], "analysis": paper[6]} for paper in papers]

    def fetch_papers_from_arxiv(self, topic: str, limit: int = 10):
        results = []
        search_query = f"all:{topic}"
        
        search = Search(query=search_query, max_results=limit, sort_by=SortCriterion.SubmittedDate)

        for result in search.results():
            published_date = result.published
            year = published_date.year if isinstance(published_date, datetime) else datetime.strptime(published_date, "%Y-%m-%d").year
            abstract = result.summary if hasattr(result, 'summary') else "No abstract available"

            paper = {
                'id': result.entry_id,
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'summary': result.summary,
                'published_date': published_date,
                'year': year,
                'topic': topic,
                'abstract': abstract,
                'detailed_analysis': ''
            }
            results.append(paper)
        return results

    def close(self):
        self.conn.close()
