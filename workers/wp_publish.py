import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

class WordPressPublisher:
    def __init__(self):
        self.wp_url = os.getenv('WP_URL', 'https://roblotech.com')
        self.wp_user = os.getenv('WP_USER', '')
        self.wp_app_password = os.getenv('WP_APP_PASSWORD', '')
        self.auth = (self.wp_user, self.wp_app_password) if self.wp_user and self.wp_app_password else None
    
    def create_post(self, title, content, status='draft', categories=None, tags=None, featured_media=None):
        """
        Create a WordPress post via REST API
        
        Args:
            title (str): Post title
            content (str): Post HTML content
            status (str): 'draft', 'publish', 'pending', 'private'
            categories (list): List of category IDs
            tags (list): List of tag IDs or tag names
            featured_media (int): Featured image ID
        
        Returns:
            dict: API response with post data
        """
        if not self.auth or not self.auth[0] or not self.auth[1]:
            return {
                'success': False,
                'error': 'WordPress credentials not configured. Set WP_USER and WP_APP_PASSWORD in .env'
            }
        
        endpoint = f"{self.wp_url}/wp-json/wp/v2/posts"
        
        post_data = {
            'title': title,
            'content': content,
            'status': status
        }
        
        if categories:
            post_data['categories'] = categories
        
        if tags:
            post_data['tags'] = tags
        
        if featured_media:
            post_data['featured_media'] = featured_media
        
        try:
            response = requests.post(
                endpoint,
                auth=self.auth,
                json=post_data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'post_id': result.get('id'),
                'post_url': result.get('link'),
                'status': result.get('status'),
                'title': result.get('title', {}).get('rendered')
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def update_post(self, post_id, title=None, content=None, status=None, categories=None):
        """Update an existing WordPress post"""
        if not self.auth or not self.auth[0] or not self.auth[1]:
            return {'success': False, 'error': 'WordPress credentials not configured'}
        
        endpoint = f"{self.wp_url}/wp-json/wp/v2/posts/{post_id}"
        
        post_data = {}
        if title:
            post_data['title'] = title
        if content:
            post_data['content'] = content
        if status:
            post_data['status'] = status
        if categories:
            post_data['categories'] = categories
        
        try:
            response = requests.post(
                endpoint,
                auth=self.auth,
                json=post_data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'post_id': result.get('id'),
                'post_url': result.get('link'),
                'status': result.get('status')
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_categories(self):
        """Fetch all WordPress categories"""
        if not self.wp_url:
            return {'success': False, 'error': 'WP_URL not configured'}
        
        endpoint = f"{self.wp_url}/wp-json/wp/v2/categories"
        
        try:
            response = requests.get(endpoint, timeout=30)
            response.raise_for_status()
            categories = response.json()
            
            return {
                'success': True,
                'categories': [{'id': cat['id'], 'name': cat['name'], 'slug': cat['slug']} for cat in categories]
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_category_id_by_name(self, category_name):
        """Get category ID by name"""
        result = self.get_categories()
        
        if not result.get('success'):
            return None
        
        for cat in result.get('categories', []):
            if cat['name'].lower() == category_name.lower() or cat['slug'] == category_name.lower():
                return cat['id']
        
        return None


def example_usage():
    """Example usage of WordPress publisher"""
    publisher = WordPressPublisher()
    
    sample_content = """
    <p>This is a sample post created via the WordPress REST API.</p>
    
    <h2>Why Automation Matters</h2>
    <p>Automating content publishing saves time and ensures consistency.</p>
    
    <h2>Key Benefits</h2>
    <ul>
        <li>Reduced manual effort</li>
        <li>Consistent publishing schedule</li>
        <li>Integration with external data sources</li>
    </ul>
    
    <h2>Getting Started</h2>
    <p>Learn how to set up WordPress REST API authentication with Application Passwords.</p>
    """
    
    result = publisher.create_post(
        title='Test Post from Automation System',
        content=sample_content,
        status='draft'
    )
    
    print(json.dumps(result, indent=2))
    
    if result.get('success'):
        print(f"\n✅ Post created successfully!")
        print(f"   Post ID: {result['post_id']}")
        print(f"   Post URL: {result['post_url']}")
        print(f"   Status: {result['status']}")
    else:
        print(f"\n❌ Error: {result.get('error')}")


if __name__ == '__main__':
    print("WordPress Publisher - Test Mode")
    print("=" * 50)
    print("\nNote: Configure WP_USER and WP_APP_PASSWORD in .env to enable publishing")
    print("\nExample usage:")
    example_usage()
