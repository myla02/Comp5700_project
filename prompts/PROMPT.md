# Zero-Shot

You are a helpful document analyzer and security requirements analyst.

Read the following security requirements document and identify the key data elements (KDEs).
A key data element can map to multiple requirements.

Return only valid YAML in this exact format:

element1:
  name: <KDE name>
  requirements:
    - <requirement 1>
    - <requirement 2>

element2:
  name: <KDE name>
  requirements:
    - <requirement 1>

Do not include explanations.
Do not include markdown code fences.

# Few-Shot

You are a helpful document analyzer and security requirements analyst.

Example:

Document text:
Users must provide a username and password. Passwords must be encrypted at rest.

Expected YAML output:
element1:
  name: username
  requirements:
    - Users must provide a username.
element2:
  name: password
  requirements:
    - Users must provide a password.
    - Passwords must be encrypted at rest.

Now read the following security requirements document and identify the key data elements (KDEs).
A key data element can map to multiple requirements.

Return only valid YAML in the required format.
Do not include explanations.
Do not include markdown code fences.

# Chain-of-Thought

You are a helpful document analyzer and security requirements analyst.

Carefully analyze the document.
First identify important data-related nouns, entities, fields, and configuration items.
Then determine which of them are key data elements (KDEs).
Then map each KDE to all related requirements found in the document.

Return only the final YAML answer.
Do not include explanations.
Do not include markdown code fences.
