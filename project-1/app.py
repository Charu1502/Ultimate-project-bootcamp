from flask import Flask, render_template, request, jsonify
import secrets as ra
import string

app = Flask(__name__)

def gen_pass(length, punctuation):
  """
  Generates a cryptographically secure, randomized password.

  Guarantees the inclusion of at least one uppercase letter, 
  one lowercase letter, one digit, and one special character.

  Args:
      length (int): The total number of characters for the password.

  Returns:
      str: The securely generated password.
  """
  basechr = string.ascii_letters + string.digits
  if punctuation:
    allowedchr = basechr + string.punctuation
    paslist = [ra.choice(string.ascii_lowercase),ra.choice(string.ascii_uppercase),ra.choice(string.digits),ra.choice(string.punctuation)]
    paslist.extend([ra.choice(allowedchr) for i in range(length-4)])
  else:
    allowedchr = basechr
    paslist = [ra.choice(string.ascii_lowercase),ra.choice(string.ascii_uppercase),ra.choice(string.digits)]
    paslist.extend([ra.choice(allowedchr) for i in range(length-3)])
  ra.SystemRandom().shuffle(paslist)
  pas = ''.join(paslist)
  return pas

@app.route("/")
def home():
  return render_template("home.html")

@app.route('/generate',methods=['POST'])
def generate():
  data = request.json
  length = int(data.get('length'))
  punctuation = data.get('punctuation')
  
  if length<8 or length>20:
    return jsonify({'error': 'Password length must be between 8 and 20 characters'})
  password = gen_pass(length, punctuation)
  return jsonify({'password': password})

if __name__=="__main__":
  app.run(debug=True)