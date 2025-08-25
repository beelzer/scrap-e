"""HTML samples for testing."""

EMPTY_HTML = ""

BASIC_HTML = """
<html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="A test page">
    </head>
    <body>
        <h1>Test Page</h1>
        <p>This is a test paragraph.</p>
    </body>
</html>
"""

COMPLEX_HTML = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Complex Test Page</title>
        <meta charset="UTF-8">
        <meta name="description" content="A complex test page">
        <meta name="keywords" content="test, complex, html">
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Article",
            "author": "Test Author",
            "datePublished": "2024-01-01"
        }
        </script>
    </head>
    <body>
        <header>
            <nav>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/about">About</a></li>
                    <li><a href="/contact">Contact</a></li>
                </ul>
            </nav>
        </header>
        <main>
            <article>
                <h1 id="main-title">Complex Test Page</h1>
                <p class="description">This is a more complex test page.</p>
                <div class="content">
                    <h2>Section 1</h2>
                    <p>Content for section 1.</p>
                    <div class="items">
                        <span data-id="1">Item 1</span>
                        <span data-id="2">Item 2</span>
                        <span data-id="3">Item 3</span>
                    </div>
                </div>
                <div class="metadata">
                    <span class="author">John Doe</span>
                    <time datetime="2024-01-01">January 1, 2024</time>
                    <span class="category">Technology</span>
                </div>
                <div class="stats">
                    <span>Views: 1,234</span>
                    <span>Likes: 567</span>
                </div>
            </article>
        </main>
        <footer>
            <p>&copy; 2024 Test Site</p>
        </footer>
    </body>
</html>
"""

TABLE_HTML = """
<html>
    <body>
        <table id="data-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Age</th>
                    <th>Email</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>John Doe</td>
                    <td>30</td>
                    <td>john@example.com</td>
                </tr>
                <tr>
                    <td>Jane Smith</td>
                    <td>25</td>
                    <td>jane@example.com</td>
                </tr>
                <tr>
                    <td>Bob Johnson</td>
                    <td>35</td>
                    <td>bob@example.com</td>
                </tr>
            </tbody>
        </table>
    </body>
</html>
"""

FORM_HTML = """
<html>
    <body>
        <form id="contact-form" action="/submit" method="post">
            <input type="text" name="name" placeholder="Name" required>
            <input type="email" name="email" placeholder="Email" required>
            <textarea name="message" placeholder="Message"></textarea>
            <select name="category">
                <option value="general">General</option>
                <option value="support">Support</option>
                <option value="sales">Sales</option>
            </select>
            <input type="checkbox" name="subscribe" value="yes">
            <button type="submit">Submit</button>
        </form>
    </body>
</html>
"""

MALFORMED_HTML = """
<html>
    <body>
        <p>Unclosed paragraph
        <div>Unclosed div
        <span>Some text</p>
        Wrong closing tag</div>
        <br>
        Price: $99.99
        Email: test@example.com
    </body>
"""

LARGE_HTML = (
    """
<html>
    <body>
        <div class="container">
"""
    + "\n".join(
        [
            f'            <p class="item-{i}">Item {i} content with some text to make it larger.</p>'
            for i in range(100)
        ]
    )
    + """
        </div>
    </body>
</html>
"""
)

# Special test cases
SPA_HTML = """
<html>
    <head>
        <title>SPA Test</title>
    </head>
    <body>
        <div id="app">Loading...</div>
        <script>
            // Simulated SPA content
            window.appData = {
                title: "Dynamic Content",
                items: ["Item 1", "Item 2", "Item 3"]
            };
        </script>
    </body>
</html>
"""

JSON_LD_HTML = """
<html>
    <head>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Test Product",
            "price": "99.99",
            "priceCurrency": "USD",
            "availability": "InStock"
        }
        </script>
    </head>
    <body>
        <h1>Product Page</h1>
    </body>
</html>
"""
