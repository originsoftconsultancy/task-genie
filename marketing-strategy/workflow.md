
# Marketing Message

## Solo Entrepreneurs, Meet Your 24/7 AI Marketing Assistant!

What if you had a digital assistant that worked round the clock, reaching the right audience, crafting personalized messages, and even following up—without you lifting a finger?

Here’s how it works:
- ✅ You provide a campaign idea (e.g., “dentists looking for better patient outreach”)
- ✅ It fetches emails & social accounts of potential leads
- ✅ It crafts targeted messages for your offer or question
- ✅ It engages with responses and continues the conversation
- ✅ It delivers real opportunities, leads, and project offers

No more cold outreach struggles. No more lost leads. Just seamless, intelligent marketing on autopilot.

# Workflows

## 1. Simple Message Broadcast

The user provides a simple prompt containing information about the audience "dentist, doctor, lawyer etc" and a campaign question or message with some other details. 

### ***Example Prompt:***

"I want to send a message to doctors about our services for HIPPA compliance dashboards that can help them focus more on their medical services instead of compliance requirements. Our website landing page is https://abc-compliance.com."

### Workflow

The system will perform the following steps in order.

- **Extract Information:** The audience is "doctors", campaign message is summarized (using LLM) with the details like links to websites, phone numbers or anything, like "https://abc-compliance.com". If audience or campaign message / question is missing, ask the user about it.

- **Get Leads:** The email leads for the given audience is fetched using the tool  `lead_search`

- **Write a Campaign Email:** A rich text HTML email is constructed (according to the email template) where campaign message or question is properly rephrased and written in professional tone (using LLM). 

- **Send Campaign Email:** The constructed email is sent to the fetched leads one by one using the tool `email_client`.

## 2. Trends Based Message Broadcast

The user provides a simple prompt containing information about the audience "dentist, doctor, lawyer etc" and asks for generating a campaign message by searching problems or trends relating to that audience. 

### ***Example Prompt:***

"I want to start a campaign for lawyers by finding trends and problems in this domain. Find our services at https://abc-financials.com".

### Workflow

The system will perform the following steps in order.

- **Extract Information:** The audience is "lawyers", campaign message is summarized (using LLM) with the details like links to websites, phone numbers or anything, like "https://abc-financials.com". If audience or campaign message / question is missing, ask the user about it.

- **Get Leads:** The email leads for the given audience is fetched using the tool  `lead_search`

- **Search for trends/problems:** Search for trends (for example using Google Trends API) or simple search results (using Serper API) to find top 5 to 10 important and latest trends or problems using the tool `insight_search`.

- **Write a Campaign Email:** A rich text HTML email is constructed (according to the email template) where campaign message is written in professional tone (using LLM) keeping the trends / problems from previous step into account. 

- **Send Campaign Email:** The constructed email is sent to the fetched leads one by one using the tool `email_client`.

## 3. Full-Duplex Communication Campaign

Besides the workflow 1 or 2, the user also wants our system to respond the email messages.

### Workflow

In addition to the steps in workflow 1 or 2, the system will perform the following,

- **Fetch Unread Emails** Fetch and filter the email responses for this campaign from the inbox.
- **Respond with LLM** Write email contents in response to the conversation. 