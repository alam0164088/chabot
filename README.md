# Sparktech AI Chatbot & Real-time Group Chat

একটি আধুনিক Django চ্যাটবট ও গ্রুপ চ্যাট অ্যাপ, যেখানে আপনি চাইলে AI (Gemini/ChatGPT) বটের সাথে চ্যাট করতে পারবেন, আবার চাইলে রিয়েল-টাইমে অন্য ইউজারদের সাথে গ্রুপ চ্যাট করতে পারবেন (Messenger-এর মতো)।

---

## ফিচারসমূহ

- 🤖 **AI Chatbot:** Gemini/ChatGPT-এর মতো AI-এর সাথে চ্যাট করুন
- 👤 **User to User Group Chat:** একাধিক ইউজার একই রুমে রিয়েল-টাইমে চ্যাট করতে পারবেন
- 🟢 **Active Users:** রুমে কে কে আছে, ডান পাশে Active Users প্যানেলে দেখাবে
- 💬 **Messenger-style History:** গ্রুপ চ্যাটে আগের মেসেজ লোকালি সেভ থাকবে, রুমে ঢুকলেই আগের কনভারসেশন দেখতে পাবেন
- 🔒 **JWT Auth:** রেজিস্ট্রেশন, লগইন, লগআউট
- 🎨 **Dark Neon UI:** সুন্দর, রেসপনসিভ, মডার্ন ডিজাইন

---

## রান করার নিয়ম

1. **রিপোজিটরি ক্লোন করুন**
2. **ডিপেন্ডেন্সি ইনস্টল করুন:**
   ```bash
   pip install -r requirements.txt
   ```
3. **মাইগ্রেশন দিন:**
   ```bash
   python manage.py migrate
   ```
4. **Daphne দিয়ে সার্ভার চালান (ASGI):**
   ```bash
   daphne -p 8000 project.asgi:application
   ```
   > ⚠️ `python manage.py runserver` দিয়ে WebSocket/Group Chat কাজ করবে না!

5. **ব্রাউজারে যান:**
   - http://127.0.0.1:8000

---

## ইউজার গাইড

- **প্রথমে রেজিস্ট্রেশন করুন, তারপর লগইন করুন।**
- **AI Chatbot মোডে:**
  - বাম পাশে চ্যাট হিস্টোরি দেখাবে
  - AI-এর সাথে চ্যাট করুন
- **User to User মোডে:**
  - রুমের নাম দিন (যেমন: lobby, nazmul-joy)
  - ডান পাশে Active Users দেখাবে
  - সবাই মেসেজ পাঠাতে পারবে, আগের মেসেজও দেখাবে (Messenger-এর মতো)
- **প্রোফাইল আইকন:** ডান উপরের কোণায়, লগআউট ও ইউজারনেম

---

## টেকনোলজি
- Django 5.x
- Django Channels 4.x (ASGI, WebSocket)
- daphne
- REST Framework, JWT
- Vanilla JS, CSS

---

## ডেভেলপার টিপস
- **WebSocket/Group Chat চালাতে হলে daphne দিয়ে সার্ভার চালান।**
- **লোকাল হিস্টোরি ব্রাউজারে সেভ হয়, চাইলে ক্লাউডে সংরক্ষণ করতে পারেন।**
- **কোডে কাস্টমাইজেশন বা নতুন ফিচার চাইলে README-র নিচে issue খুলুন!**

---

## কন্ট্রিবিউশন
Pull request, issue, ফিচার সাজেশন স্বাগত!

---

## লাইসেন্স
MIT
