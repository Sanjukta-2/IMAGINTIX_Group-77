const Contact = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted flex items-center justify-center p-6">
      
      <div className="w-full max-w-2xl bg-card border border-border rounded-2xl shadow-xl p-8">
        
        <h1 className="text-4xl font-bold text-center mb-6">
          Contact Us
        </h1>

        <p className="text-center text-muted-foreground mb-8">
          We'd love to hear from you. Reach out to us anytime!
        </p>

        {/* Contact Info */}
        <div className="space-y-4 mb-8">
          <div className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
            <span className="font-semibold">📧 Email</span>
            <span className="text-muted-foreground">
              mahikaroy2004@gmail.com
            </span>
          </div>

          <div className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
            <span className="font-semibold">📞 Phone</span>
            <span className="text-muted-foreground">
              +91 9289291121
            </span>
          </div>

          <div className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
            <span className="font-semibold">📍 Location</span>
            <span className="text-muted-foreground">
              Kolkata, India
            </span>
          </div>
        </div>

        {/* Contact Form (Dummy UI) */}
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Your Name"
            className="w-full p-3 rounded-lg border border-border bg-background"
          />

          <input
            type="email"
            placeholder="Your Email"
            className="w-full p-3 rounded-lg border border-border bg-background"
          />

          <textarea
            placeholder="Your Message"
            rows={4}
            className="w-full p-3 rounded-lg border border-border bg-background"
          />

          <button
            className="w-full bg-primary text-primary-foreground py-3 rounded-lg font-semibold hover:opacity-90 transition"
            onClick={() => alert("Message sent (dummy)")}
          >
            Send Message
          </button>
        </div>
      </div>
    </div>
  );
};

export default Contact;