# Tracker: local Markdown

This repo's specs and tickets live as Markdown files in `.scratch/`.

## Conventions

- One feature per folder: `.scratch/<feature-slug>/`.
- The spec is `.scratch/<feature-slug>/spec.md`.
- Implementation tickets are one file per ticket in `.scratch/<feature-slug>/tickets/<NN>-<slug>.md`, numbered from `01`. Never a single file with every ticket.
- The status goes in a `Status:` line near the top of each file. Values: `ready-for-agent`, `ready-for-human`, `in-progress`, `done`, `discarded`.
- Dependencies go in a `Blocked by:` line with the numbers of the tickets that block it, or `None`.
- Comments and history are appended at the end under a `## Comments` heading, with a date.

## When a skill says "publish to the tracker"

Create the file inside `.scratch/<feature-slug>/`, creating the folder if needed.

## When a skill says "fetch the ticket"

Read the file at the given path. Usually the user passes the path or the ticket number.

## Work frontier

A ticket is **unblocked** when every ticket listed in `Blocked by:` is `done`. The frontier is the unblocked tickets that are neither `in-progress` nor `done`; the lowest number wins. When you start one, change its status to `in-progress` and save before working.
