from flask import Flask, render_template_string, request, redirect, url_for, session, flash, send_from_directory
import json, os

from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

USER_FILE = "users.json"
JOB_FILE = "pickup_requests.json"

if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

if os.path.exists(JOB_FILE):
    with open(JOB_FILE, "r") as f:
        pickup_requests = json.load(f)
else:
    pickup_requests = []

HTML_HEAD = """
<!DOCTYPE html>
<html>
<head>
<title>Bin for a Buck</title>
<style>
input, select, textarea {
    width: 100%;
    padding: 10px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 5px;
    box-sizing: border-box;
}
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background: linear-gradient(to bottom right, #e3f2fd, #bbdefb);
    color: #333;
}
header {
    background-color: #007bff;
    color: white;
    padding: 20px 10px;
    text-align: center;
}
.nav {
    background-color: #f8f9fa;
    padding: 10px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.nav a {
    margin: 0 15px;
    text-decoration: none;
    font-weight: bold;
    color: #007bff;
}
.container {
    max-width: 800px;
    margin: 30px auto;
    padding: 20px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
h1, h2, h3 {
    margin-bottom: 10px;
}
ul {
    list-style-type: none;
    padding-left: 0;
}
ul li {
    margin: 8px 0;
}
button {
    background: #28a745;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
}
button:hover {
    background: #218838;
}
</style>
<script>
function toggleEdit(jobIndex) {
    var editForm = document.getElementById('edit-form-' + jobIndex);
    if (editForm.style.display === 'none') {
        editForm.style.display = 'block';
    } else {
        editForm.style.display = 'none';
    }
}
</script>
</head>
<body>
<header>
    <h1>🗑️ Bin for a Buck</h1>
</header>
<div class="nav">
    <a href="/">Home</a>
    <a href="/signup">Sign Up</a>
    <a href="/login">Login</a>
    <a href="/logout">Logout</a>
    <a href="/request">Request Pickup</a>
    <a href="/jobs">View Jobs</a>
</div>
"""

HTML_FOOT = """
<footer style="text-align:center; font-size:12px; color:gray; margin-top:50px; padding:15px;">
    © 2025 Bin for a Buck. All rights reserved.<br>
    Contact: <a href="mailto:kfirslon@gmail.com">kfirslon@gmail.com</a>
</footer>
</body></html>
"""



DISCLAIMER = """
<div style='margin-top:40px; padding:15px; background:#fff0f0; border-left:4px solid red;'>
⚠️ Please use common sense when meeting or paying neighbors. Bin for a Buck is a community platform and not liable for interactions.
</div>
"""


@app.route('/')
def home():
    welcome_message = f"<p>Hello, {session['user']['name']}!</p>" if 'user' in session else ""
    return render_template_string(HTML_HEAD + f"""
    <div class="container">
        {welcome_message}
        <h2>A Community Solution for Helping Each Other with Garbage Pickup</h2>
        <p>Need help with your garbage? Request a pickup from a neighbor for just a buck (or up to $10)!</p>

        <div style='margin-top:30px; padding:15px; background:#e9f7fe; border-left:5px solid #007bff; border-radius: 8px;'>
            🤖 <strong>Coming Soon:</strong> AI-powered pickup suggestions, route optimization, and personalized recommendations.
        </div>

        <div style='margin-top:30px;'>
            <h3 style="color:#007bff;">What is Bin for a Buck?</h3>
            <p><strong>Bin for a Buck</strong> is a community-based solution for high-rise residents who need help taking out the trash. Post your pickup, and a neighbor can help — all for just $1 to $10.</p>
            <ul>
                <li>✅ Save time and energy</li>
                <li>🚫 No more hauling smelly garbage down 10 flights</li>
                <li>👥 Let your neighbors help — and earn a buck!</li>
                <li>📲 Simple, fast, and effective</li>
            </ul>
        </div>
    </div>
    """ + HTML_FOOT)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email'].lower()
        password = request.form['password']
        if email in users:
            flash("Email already registered.")
        else:
            users[email] = {'name': name, 'password': password}
            with open(USER_FILE, "w") as f:
                json.dump(users, f)
            flash("Signed up! Please log in.")
            return redirect(url_for('login'))
    return render_template_string(HTML_HEAD + """
    <h2>Sign Up</h2>
    <form method="POST">
        <div class="form-group"><label>Name:</label><input name="name" required></div>
        <div class="form-group"><label>Email:</label><input name="email" type="email" required></div>
        <div class="form-group"><label>Password:</label><input name="password" type="password" required></div>
        <button>Sign Up</button>
    </form>
    """ + HTML_FOOT)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        user = users.get(email)
        if user and user['password'] == password:
            session['user'] = {'email': email, 'name': user['name']}
            flash(f"Hello, {user['name']}! Welcome back.")
            return redirect(url_for('home'))
        flash("Invalid login.")
    return render_template_string(HTML_HEAD + """
    <h2>Login</h2>
    <form method="POST">
        <div class="form-group"><label>Email:</label><input name="email" required></div>
        <div class="form-group"><label>Password:</label><input name="password" type="password" required></div>
        <button>Log In</button>
    </form>
    """ + HTML_FOOT)


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out.")
    return redirect(url_for('home'))


@app.route('/request', methods=['GET', 'POST'])
def request_pickup():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        photo = request.files.get('photo')
        filename = ""
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        pickup_requests.append({
            'name': request.form['name'],
            'email': session['user']['email'],
            'accepted_by': None,
            'accepted_by_email': None,
            'ratings': [],
            'location': request.form['location'],
            'floor': request.form['floor'],
            'bags': request.form['bags'],
            'pickup_time': request.form['pickup_time'],
            'notes': request.form['notes'],
            'contact': request.form['contact'],
            'price': request.form['price'],
            'card_info': request.form['card_info'],
            'photo': filename,
            'picked_up': False
        })
        with open(JOB_FILE, "w") as f:
            json.dump(pickup_requests, f)

        return redirect(url_for('view_jobs'))

    return render_template_string(HTML_HEAD + f"""
    <div class="container">
        <h2 style="color:#007bff;">🚛 Request a Pickup</h2>
        <p>Fill in the details below to request help from a neighbor.</p>
        <form method="POST" enctype="multipart/form-data" style="text-align:left;">
            <div class="form-group" style="margin-bottom: 15px;">
                <label><strong>Name (First and Last):</strong></label>
                <input name="name" value="{session['user']['name']}" required>
            </div>
            <div class="form-group" style="margin-bottom: 15px;">
                <label><strong>Location (Include Apt Number):</strong></label>
                <input name="location" required>
            </div>
            <div class="form-group" style="margin-bottom: 15px;">
                <label><strong>Floor:</strong></label>
                <input name="floor" required>
            </div>
            <div class="form-group" style="margin-bottom: 15px;">
                <label><strong>Number of Bags:</strong></label>
                <input name="bags" required>
            </div>
            <div class="form-group" style="margin-bottom: 15px;">
                <label><strong>Pickup Time:</strong></label>
                <input name="pickup_time" placeholder="e.g. Tuesday, 10:30 AM" required>
            </div>
            <div class="form-group" style="margin-bottom: 15px;">
                <label><strong>Notes:</strong></label>
                <textarea name="notes" placeholder="Optional extra info..."></textarea>
            </div>
            <div class="form-group" style="margin-bottom: 15px;">
                <label><strong>Contact Info (Phone/Email):</strong></label>
                <input name="contact" required>
            </div>
            <div class="form-group" style="margin-bottom: 15px;">
                <label><strong>Tip (Optional):</strong></label>
                <select name="tip" required>
                    <option value="" disabled selected>Select an amount</option>
                    <option value="1">$1</option>
                    <option value="2">$2</option>
                    <option value="5">$5</option>
                    <option value="10">$10</option>
                </select>
                <small style="display:block; margin-top:5px;">Tipping is appreciated but not required.</small>
            </div>
            <div class="form-group" style="margin-bottom: 20px;">
                <label><strong>Photo:</strong></label>
                <input type="file" name="photo">
            </div>
            <button type="submit" style="width: 100%; font-size: 16px;">📬 Submit Request</button>
        </form>
    </div>
    """ + HTML_FOOT)


@app.route('/jobs', methods=['GET', 'POST'])
def view_jobs():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        index = int(request.form['job_index'])
        if 'accept' in request.form:
            pickup_requests[index]['accepted_by'] = session['user']['name']
            pickup_requests[index]['accepted_by_email'] = session['user'][
                'email']
        elif 'unaccept' in request.form:
            pickup_requests[index]['accepted_by'] = None
            pickup_requests[index]['accepted_by_email'] = None
        elif 'toggle_pickup' in request.form:
            pickup_requests[index][
                'picked_up'] = not pickup_requests[index].get(
                    'picked_up', False)
        elif 'rating' in request.form:
            rating = int(request.form['rating'])
            pickup_requests[index]['ratings'].append(rating)
        elif 'edit' in request.form:
            # Update job with new information
            pickup_requests[index]['location'] = request.form['location']
            pickup_requests[index]['floor'] = request.form['floor']
            pickup_requests[index]['bags'] = request.form['bags']
            pickup_requests[index]['pickup_time'] = request.form['pickup_time']
            pickup_requests[index]['notes'] = request.form['notes']
            pickup_requests[index]['contact'] = request.form['contact']
            pickup_requests[index]['price'] = request.form['price']
        elif 'delete' in request.form:
            pickup_requests.pop(index)

        with open(JOB_FILE, "w") as f:
            json.dump(pickup_requests, f)

    job_list = HTML_HEAD + """
    <h2>Available Pickups</h2>
    <div style="margin-bottom:20px;">
        <span style="display:inline-block; width:15px; height:15px; background:#ffd180; border:1px solid #ff9100; margin-right:5px;"></span> Waiting
        &nbsp;&nbsp;
        <span style="display:inline-block; width:15px; height:15px; background:#81d4fa; border:1px solid #0288d1; margin-right:5px;"></span> Accepted
        &nbsp;&nbsp;
        <span style="display:inline-block; width:15px; height:15px; background:#a5d6a7; border:1px solid #388e3c; margin-right:5px;"></span> Picked Up
    </div>
    """

    for i, job in enumerate(pickup_requests):
        if job.get('picked_up'):
            job_class = "picked-up"
            job_style = "background:#a5d6a7; border-left:5px solid #388e3c;"
        elif job.get('accepted_by'):
            job_class = "accepted"
            job_style = "background:#81d4fa; border-left:5px solid #0288d1;"
        else:
            job_class = "waiting"
            job_style = "background:#ffd180; border-left:5px solid #ff9100;"

        job_list += f"""
    <div class='job-box {job_class}' style="{job_style} text-align:left; padding:20px; margin-bottom:25px; border-radius:10px;">
            <div style="font-size:18px; font-weight:bold; margin-bottom:10px; color:#007bff;">{job['name']} — {'Free' if job.get('price') in ['0', 0, 'Free'] else f"${job.get('price')}"}
    </div>
            <div style="margin-bottom:10px;">
                📍 <strong>Location:</strong> {job.get('location', 'N/A')}<br>
                🏢 <strong>Floor:</strong> {job['floor']} &nbsp; | &nbsp; 🛍️ <strong>Bags:</strong> {job['bags']}<br>
                ⏰ <strong>Time:</strong> {job.get('pickup_time', '')}<br>
                📝 <strong>Notes:</strong> {job['notes']}<br>
                📞 <strong>Contact:</strong> {job.get('contact', 'Not provided')}<br>
                🤝 <strong>Status:</strong> {job['accepted_by'] if job['accepted_by'] else 'Available'}
            </div>
            {f'<img src="/static/uploads/{job["photo"]}" style="margin-top:10px; max-width:200px; border-radius:5px;">' if job.get("photo") else ""}

            <div style="margin-top:15px;">
                <!-- Accept Job -->
                {f'''
                <form method="POST" style="display:inline;">
                    <input type="hidden" name="job_index" value="{i}">
                    <button type="submit" name="accept">✅ Accept This Job</button>
                </form>''' if not job['accepted_by'] and job['email'] != session['user']['email'] else ''}

                <!-- Unaccept -->
                {f'''
                <form method="POST" style="display:inline;">
                    <input type="hidden" name="job_index" value="{i}">
                    <button type="submit" name="unaccept" style="background:#dc3545;">Remove Myself</button>
                </form>''' if job.get('accepted_by_email') == session['user']['email'] and not job.get('picked_up') else ''}

                <!-- Mark as picked up / Cancel -->
                {f'''
                <form method="POST" style="display:inline;">
                    <input type="hidden" name="job_index" value="{i}">
                    <button type="submit" name="toggle_pickup">
                        {"Cancel Pickup" if job.get("picked_up") else "Mark as Picked Up"}
                    </button>
                </form>''' if session['user']['email'] in [job['email'], job.get('accepted_by_email')] else ''}

                <!-- Rate -->
                {f'''
                <form method="POST" style="margin-top:10px;">
                    <input type="hidden" name="job_index" value="{i}">
                    <label>⭐ Rate Helper (1–5):</label>
                    <select name="rating">{"".join([f"<option>{r}</option>" for r in range(1, 6)])}</select>
                    <button type="submit">Submit</button>
                </form>''' if job.get("picked_up") and job['email'] == session['user']['email'] and job.get('accepted_by') else ''}

                <!-- Message -->
                {f"<a href='mailto:{job['contact']}'><button style='background:#17a2b8;'>📩 Message</button></a>" if job['email'] != session['user']['email'] else ''}

                <!-- Edit -->
                {f'''
                <button onclick="toggleEdit({i})" style="background:#ffc107;">✏️ Edit</button>
                <div id="edit-form-{i}" style="display:none; margin-top:10px;">
                    <form method="POST">
                        <input type="hidden" name="job_index" value="{i}">
                        <label>Location:</label><input name="location" value="{job.get('location', '')}" required><br>
                        <label>Floor:</label><input name="floor" value="{job['floor']}" required><br>
                        <label>Bags:</label><input name="bags" value="{job['bags']}" required><br>
                        <label>Time:</label><input name="pickup_time" value="{job.get('pickup_time', '')}" required><br>
                        <label>Notes:</label><textarea name="notes">{job['notes']}</textarea><br>
                        <label>Contact:</label><input name="contact" value="{job.get('contact', '')}" required><br>
                        <label>Price:</label>
                        <select name="price">{"".join([f'<option {"selected" if str(job.get("price")) == str(p) else ""}>{p}</option>' for p in range(1, 11)])}</select><br>
                        <button type="submit" name="edit">Update</button>
                        <button type="button" onclick="toggleEdit({i})">Cancel</button>
                    </form>
                </div>''' if job['email'] == session['user']['email'] and not job.get('accepted_by') else ''}

                <!-- Delete -->
                {f'''
                <form method="POST" style="display:inline;">
                    <input type="hidden" name="job_index" value="{i}">
                    <button type="submit" name="delete" style="background:#dc3545;">🗑️ Delete</button>
                </form>''' if job['email'] == session['user']['email'] else ''}
            </div>
        </div>
        """

    return render_template_string(job_list + DISCLAIMER + HTML_FOOT)


@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
