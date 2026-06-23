# Implement ENABLE_MID in Markdown

## WHAT

Enable the `ENABLE_MID` behavior in Markdown similar how it is done by the SDoc machinery.

## WHY

The `ENABLE_MID` feature is very important for many users. We want to have it enabled for Markdown.

At the same time, we would like to avoid adding a yet another document-level option to active it.

The automatic recognition based on the grammar field should be enough to do the job.
