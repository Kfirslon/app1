
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
<!DOCTYPE html><html><head><title>Bin for a Buck</title>
<style>
body { font-family: Arial; padding: 20px; background: #fff; }
.nav a { margin-right: 15px; text-decoration: none; font-weight: bold; color: #007bff; }
.form-group { margin-bottom: 10px; }
input, select, textarea { width: 100%; padding: 8px; }
.job-box { background: #f9f9f9; padding: 10px; border-left: 4px solid #007bff; margin-bottom: 10px; }
.picked-up { background: #e6ffe6; border-left: 4px solid #28a745; }
.accepted {
    background-color: #fffbe6;
    border-left: 4px solid orange;
}
button { background: #28a745; color: white; border: none; padding: 8px 12px; cursor: pointer; }
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
</head><body>
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
</body></html>
"""

DISCLAIMER = """
<div style='margin-top:40px; padding:15px; background:#fff0f0; border-left:4px solid red;'>
⚠️ Please use common sense when meeting or paying neighbors. Bin for a Buck is a community platform and not liable for interactions.
</div>
"""


@app.route('/')
def home():
    return render_template_string(HTML_HEAD + """
    <h1>🗑️ Welcome to Bin for a Buck</h1>
    <p>Need help with your garbage? Request a pickup from a neighbor for just a buck (or up to $10)!</p>
    <div style='margin-top:30px; padding:15px; background:#f0f8ff; border-left:5px solid #007bff;'>
        🤖 <strong>Coming Soon:</strong> AI-powered pickup suggestions, route optimization, and personalized recommendations.
    </div>
    <div style='margin-top:30px; background:#fefefe; padding:20px; border-radius:10px; box-shadow: 0 0 5px rgba(0,0,0,0.05);'>
        <h3>What is Bin for a Buck?</h3>
        <p><strong>Bin for a Buck</strong> is a community-based solution for high-rise residents who need help taking out the trash. Post your pickup, and a neighbor can help — all for just $1 to $10.</p>
        <ul>
            <li>✅ Save time and energy</li>
            <li>🚫 No more hauling smelly garbage down 10 flights</li>
            <li>👥 Let your neighbors help — and earn a buck!</li>
            <li>📲 Simple, fast, and effective</li>
        </ul>
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

    return render_template_string(HTML_HEAD + """
    <h2>Request Pickup</h2>
    <form method="POST" enctype="multipart/form-data">
        <div class="form-group"><label>Name (First and Last):</label><input name="name" required></div>
        <div class="form-group"><label>Location (Zip or Building):</label><input name="location" required></div>
        <div class="form-group"><label>Floor:</label><input name="floor" required></div>
        <div class="form-group"><label>Number of Bags:</label><input name="bags" required></div>
        <div class="form-group"><label>Pickup Time (e.g. 10:30 AM or 2:15 PM):</label><input name="pickup_time" required></div>
        <div class="form-group"><label>Notes:</label><textarea name="notes"></textarea></div>
        <div class="form-group"><label>Contact Info (Phone/Email):</label><input name="contact" required></div>
        <div class="form-group"><label>Price ($):</label>
        <select name="price">""" + ''.join([f"<option>{i}</option>" for i in range(1, 11)]) + """</select></div>
        <div class="form-group"><label>Credit Card Info:</label><input name="card_info" required></div>
        <div class="form-group"><label>Photo:</label><input type="file" name="photo"></div>
        <button>Submit Request</button>
    </form>
    """.format(session['user']['name']) + HTML_FOOT)

@app.route('/jobs', methods=['GET', 'POST'])
def view_jobs():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        index = int(request.form['job_index'])
        if 'accept' in request.form:
            pickup_requests[index]['accepted_by'] = session['user']['name']
            pickup_requests[index]['accepted_by_email'] = session['user']['email']
        elif 'unaccept' in request.form:
            pickup_requests[index]['accepted_by'] = None
            pickup_requests[index]['accepted_by_email'] = None
        elif 'toggle_pickup' in request.form:
            pickup_requests[index]['picked_up'] = not pickup_requests[index].get('picked_up', False)
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

    job_list = HTML_HEAD + "<h2>Available Pickups</h2>"

    for i, job in enumerate(pickup_requests):
        if job.get('picked_up'):
            job_class = "picked-up"
        elif job.get('accepted_by'):
            job_class = "accepted"
        else:
            job_class = ""

        job_list += f"""
        <div class='job-box {job_class}'>
            <strong>{job['name']}</strong> – ${job.get('price', '?')}<br>
            Location: {job.get('location', 'N/A')}<br>
            Floor: {job['floor']}<br>
            Bags: {job['bags']}<br>
            Time: {job.get('pickup_time', '')}<br>
            Notes: {job['notes']}<br>
            Contact: {job.get('contact', 'Not provided')}<br>
            Accepted by: {job['accepted_by'] if job['accepted_by'] else 'Available'}<br>
            {'<img src="/static/uploads/' + job['photo'] + '" style="margin-top:10px; max-width:200px;">' if job.get("photo") else ""}

                <!-- Accept Job (if not accepted and not your own) -->
            {f'''
            <form method="POST">
                <input type="hidden" name="job_index" value="{i}">
                <button type="submit" name="accept">Accept This Job</button>
            </form>''' if not job['accepted_by'] and job['email'] != session['user']['email'] else ''}

                <!-- Unaccept Job (if you accepted it but haven't picked up yet) -->
            {f'''
            <form method="POST">
                <input type="hidden" name="job_index" value="{i}">
                <button type="submit" name="unaccept" style="background: #dc3545;">Remove Myself from Job</button>
            </form>''' if job.get('accepted_by_email') == session['user']['email'] and not job.get('picked_up') else ''}

                <!-- Mark as picked up / Cancel -->
            {f'''
            <form method="POST">
                <input type="hidden" name="job_index" value="{i}">
                <button type="submit" name="toggle_pickup">
                    {"Cancel Pickup" if job.get("picked_up") else "Mark as Picked Up"}
                </button>
            </form>''' if session['user']['email'] in [job['email'], job.get('accepted_by_email')] else ''}

                <!-- Rate the helper -->
            {f'''
            <form method="POST">
                <input type="hidden" name="job_index" value="{i}">
                <label>Rate Helper (1–5):</label>
                <select name="rating">
                    {''.join([f"<option>{r}</option>" for r in range(1, 6)])}
                </select>
                <button type="submit">Submit Rating</button>
            </form>''' if job.get("picked_up") and job['email'] == session['user']['email'] and job.get('accepted_by') else ''}

                <!-- Message button (email) -->
            {f"<a href='mailto:{job['contact']}'><button>Message</button></a>" if job['email'] != session['user']['email'] else ''}

                <!-- Edit Job (only for job creator and if not accepted yet) -->
            {f'''
            <button onclick="toggleEdit({i})" style="background:#007bff; margin-top:10px;">Edit Job</button>
            <div id="edit-form-{i}" style="display:none; margin-top:10px; padding:10px; background:#f0f8ff; border-radius:5px;">
                <strong>Edit Job:</strong>
                <form method="POST">
                    <input type="hidden" name="job_index" value="{i}">
                    <div style="margin:5px 0;"><label>Location:</label><input name="location" value="{job.get('location', '')}" required></div>
                    <div style="margin:5px 0;"><label>Floor:</label><input name="floor" value="{job['floor']}" required></div>
                    <div style="margin:5px 0;"><label>Bags:</label><input name="bags" value="{job['bags']}" required></div>
                    <div style="margin:5px 0;"><label>Pickup Time:</label><input name="pickup_time" value="{job.get('pickup_time', '')}" required></div>
                    <div style="margin:5px 0;"><label>Notes:</label><textarea name="notes">{job['notes']}</textarea></div>
                    <div style="margin:5px 0;"><label>Contact:</label><input name="contact" value="{job.get('contact', '')}" required></div>
                    <div style="margin:5px 0;"><label>Price ($):</label>
                    <select name="price">''' + ''.join([f'<option {"selected" if str(job.get("price")) == str(p) else ""}>{p}</option>' for p in range(1, 11)]) + f'''</select></div>
                    <button type="submit" name="edit" style="background:#007bff;">Update Job</button>
                    <button type="button" onclick="toggleEdit({i})" style="background:#6c757d;">Cancel</button>
                </form>
            </div>''' if job['email'] == session['user']['email'] and not job.get('accepted_by') else ''}

                <!-- Delete button -->
            {f'''
            <form method="POST">
                <input type="hidden" name="job_index" value="{i}">
                <button type="submit" name="delete" style="background:#dc3545;">Delete Job</button>
            </form>''' if job['email'] == session['user']['email'] else ''}
        </div>
        """
    return render_template_string(job_list + DISCLAIMER + HTML_FOOT)

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
