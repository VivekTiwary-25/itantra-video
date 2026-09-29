The video demo should use **three dedicated iTantra demo builds**, one for each phone/person shown in the film:

- Vachana’s phone
- Yash’s phone
- Vivek’s phone

All three should look like the **same iTantra app**. They are not three different products.

The reason for having three separate builds is reliability during filming. Each phone only needs to perform the exact sequence required for that actor, with the correct notifications, messages and UI states appearing at the right time.

The apps can therefore use deterministic/preloaded demo states behind the scenes, while the visible UI should behave naturally and look like the real product.

The viewer should never see labels such as “demo app,” “simulation,” “mock,” “Vachana build,” etc.

---

## 1. Vachana’s app

Vachana’s phone has the largest role because she starts both demo paths.

It needs to support four moments:

1. Send a normal private message to Yash.
2. Receive Yash’s reply.
3. Send an SOS request.
4. Receive Vivek’s response.

### Normal-message flow

Vachana starts on the normal iTantra home screen.

She should be able to:

- choose the language;
- choose Push-to-Talk;
- hold/speak;
- finish recording;
- briefly show a transcription/loading state;
- receive a preloaded/deterministic transcription;
- review/edit it in the composer;
- keep the message type as Normal;
- select Yash as the trusted recipient;
- tap Send;
- see a believable send/success state.

The exact message text is not important.

The important visible workflow is:

**PTT → transcription → review → Normal → Yash → Send**

After sending, the video leaves the app and shows the campus/relay visualisation.

### Receiving Yash’s reply

Later, while Vachana is doing something else, her phone needs to receive a believable Android notification from iTantra.

When she taps it:

- iTantra opens;
- she lands in Logs or the relevant conversation;
- the incoming reply is visible;
- she can open/read it normally.

She does not need to send another reply.

That closes the normal-message path.

---

## 2. Vachana’s SOS flow

Later in the video, the same Vachana app demonstrates SOS.

This should visibly feel like the same app, not a separate emergency application.

For this part she uses **Hands-free** instead of Push-to-Talk.

The workflow should be:

**Hands-free → listening → speech recognised → review → select SOS → Send**

When SOS is selected, the UI should visibly behave differently from a normal private message.

For a normal message, Vachana chooses a trusted recipient such as Yash.

For SOS, she should not need to choose one specific trusted contact.

The recipient-selection behaviour should therefore disappear/change appropriately when SOS is active.

After she taps Send, show a useful state such as:

- searching for nearby responders;
- SOS active;
- looking for nearby help;

or equivalent wording.

The exact wording is flexible.

---

## 3. Vachana receives Vivek’s SOS response

After Vivek accepts and responds, Vachana’s phone should receive another real-looking Android notification.

She taps it and sees the SOS/conversation in iTantra.

The response is visible.

That is where the emergency story ends.

She does not need to send another message.

---

# 4. Yash’s app

Yash’s build only needs to handle the normal private-message path.

Its job is:

1. receive Vachana’s private message;
2. let Yash hear it using TTS;
3. let Yash reply.

Before the notification arrives, Yash should **not** already be inside iTantra.

During filming he should be using his phone normally, preferably scrolling Instagram.

Then the iTantra notification appears over whatever he is doing.

This is important because it makes the app feel like a normal background communication application rather than a staged screen demo.

---

## 5. Yash receives Vachana’s message

The Yash build needs to trigger/show a believable Android notification at the appropriate moment.

When Yash taps the notification:

- iTantra opens;
- he reaches Logs or the relevant conversation;
- the incoming message is visible;
- he opens the message.

The exact incoming message text does not matter.

It only needs to match what Vachana supposedly sent in the filmed sequence.

---

## 6. Yash plays the TTS

Inside the received-message view, there should be a clear Play/audio control.

Yash taps Play.

The app plays the prepared/captured TTS output.

This is one of the important proof moments in the video, so the TTS state needs to look convincing and be easy to film.

The editor will reduce music/narration during this moment so the actual TTS can be heard clearly.

---

## 7. Yash replies

After listening, Yash should be able to respond.

Preferred visible workflow:

**PTT → transcription/review → Send**

Vachana can already be selected as the reply recipient because he is replying inside the conversation.

The exact reply text is not important.

After Send, Yash’s job in the demo is complete.

The Vachana app then receives the corresponding notification/reply.

---

# 8. Vivek’s app

Vivek’s build is specifically for the SOS responder path.

Its job is:

1. receive an SOS while Vivek is using his phone normally;
2. show Accept / Decline;
3. allow Vivek to accept;
4. open the SOS inside iTantra;
5. allow Vivek to reply;
6. cause Vachana’s app to receive the response.

Vivek is **not a trusted contact** in this scenario.

That distinction is important.

---

## 9. Vivek before the SOS

Before the alert appears, Vivek should be doing something completely unrelated to iTantra.

The planned filming gag is to have ChatGPT open with something silly/mundane such as:

**“How can I make money selling momos?”**

The exact prompt is not important.

The point is simply that he is using his phone normally when a serious emergency notification interrupts him.

---

# 10. Vivek’s SOS notification

The incoming notification should clearly feel different from a normal trusted message.

It should communicate something like:

**SOS**  
**Someone nearby needs help**

and provide two actions:

**Accept**  
**Decline**

This is critical.

Because Vivek is not already a trusted recipient, the SOS should not automatically open as though he had already agreed to participate.

For the filmed path, Vivek taps **Accept**.

---

# 11. After Vivek accepts

After Accept:

- iTantra opens;
- Vivek can see the SOS in Logs / an emergency conversation;
- he can open the request;
- the request content is readable;
- reply controls are available.

There is no need for:

- six-digit verification;
- additional identity-confirmation scenes;
- technical networking screens;
- debug information.

Keep the interaction simple and cinematic.

---

# 12. Vivek replies

Vivek can respond using whichever filming path works best:

- Push-to-Talk; or
- Hands-free.

The workflow should be approximately:

**input mode → speech → transcription/review → Send**

The exact response wording is not important.

It just needs to communicate that Vivek has acknowledged the request and is responding/helping.

After Send, the Vachana build should be ready to show the corresponding incoming notification and response.

---

# 13. How the three builds relate to each other

These are **three actor-specific demo builds of one product**.

They should share the same:

- visual design;
- colour palette;
- typography;
- Home screen;
- Logs UI;
- message-detail UI;
- composer;
- PTT controls;
- Hands-free controls;
- Normal / SOS behaviours;
- notification branding.

The viewer should have no reason to suspect that different dedicated builds are being used.

Internally, however, each build can have exactly the deterministic behaviour needed for filming.

That is desirable.

We are optimizing for a reliable filmed demonstration, not trying to make the actors depend on fragile live networking during every take.

---

# 14. Synchronisation between the three apps

The simplest reliable approach is acceptable.

For example, the apps may use:

- predefined messages;
- scripted state transitions;
- manually triggered incoming messages;
- timed notifications;
- hidden developer/demo triggers;
- local state;
- another simple deterministic mechanism.

Claude should choose the simplest robust implementation that makes filming predictable.

The visible behaviour is what matters.

A failed take because the actual radio/network state did something unexpected is much worse than using controlled demo-state plumbing.

---

# 15. Notifications matter a lot

The incoming messages should appear as believable Android notifications because this is how the live-action scenes transition from ordinary phone use into iTantra.

Required notification moments:

1. Yash receives Vachana’s normal message.
2. Vachana receives Yash’s reply.
3. Vivek receives the SOS with Accept / Decline.
4. Vachana receives Vivek’s SOS response.

The notification behaviour should be easy to trigger repeatedly during filming.

---

# 16. Exact message text is deliberately not locked

Do not over-engineer the builds around specific sentences.

The important things are:

- who is sending;
- who is receiving;
- whether it is Normal or SOS;
- trusted-contact behaviour;
- Accept / Decline behaviour;
- PTT vs Hands-free;
- transcription/review;
- TTS;
- Logs;
- Send;
- incoming notifications.

The actual message wording can be chosen later based on whichever take/audio works best.

---

# 17. What each phone needs, in one line

**Vachana phone:**  
Normal send → receive Yash reply → SOS send → receive Vivek response.

**Yash phone:**  
Receive normal message → open Logs → play TTS → reply.

**Vivek phone:**  
Receive SOS while using another app → Accept / Decline → Accept → open SOS → reply.

---

# 18. What must NOT happen

Do not build or depict:

- relay phones displaying private message contents;
- Vivek being shown as an existing trusted contact;
- SOS being automatically accepted;
- Vivek receiving SOS as an ordinary trusted message;
- actors already waiting inside iTantra when notifications arrive;
- six-digit verification;
- visible debug/developer controls;
- “demo,” “mock,” or “simulation” labels;
- unnecessary technical setup steps during the filmed workflow.

---

# 19. Development / delivery expectation

Build these as three dedicated actor-specific variants in whatever maintainable way is simplest.

Prefer shared code/components with actor-specific configuration or branches rather than independently duplicating the whole app three times unless there is a strong practical reason.

The builds should be committed/pushed to Git so they can be retrieved and installed later without requiring all three phones to stay connected while development is happening.

The end goal is simple:

**Vachana, Yash and Vivek should each have an iTantra build that reliably performs only the exact sequence required for their part of the video, while all three appear to the viewer to be the same real iTantra application.**