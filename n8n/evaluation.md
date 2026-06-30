 n8n vs Code-Based Agent-Evaluation

 What was built
A simple n8n flow: Manual Trigger -> HTTP Request (Yahoo Finance chart API for AAPL)
returning live price data as JSON.

 Comparison

| | Python Agent | n8n |
|---|---|---|
| Setup time | Fast (pip install) | Local install failed (native build error); used n8n cloud instead |
| Error handling | Explicit, written in code (retries, empty-data check) | Built-in node retry settings, less visible/customizable than code |
| Debugging | Print statements, full control | Visual execution trace, easy to see where data flows/breaks |
| Reusability | Function callable from anywhere, scriptable | Tied to n8n's UI/cloud, harder to integrate into other code |
| Best for | Repeatable batch downloads across many tickers | Quick prototyping / visual demo of a flow |

 Takeaway
The Python agent is more practical for downloading 100+ tickers at scale ‚AI
easy to loop, log, and extend. n8n is faster to demo visually and is useful for
non-technical stakeholders to see the flow, but the local installation issues
made it less reliable to set up than the Python route.
