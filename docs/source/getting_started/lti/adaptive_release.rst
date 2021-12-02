Adaptive Release
================

When uploading a split document, or a Chirun "course package" consisting of multiple documents, Chirun allows you to adaptively
release content, hiding the content from learners until a certain date/time has passed or the content is manually released.

To access the adaptive release settings, select "Access Control" at the top of the instructor dashboard, then "Adaptive Release".
If your LTI item has multiple pieces of content associated with it, they will be shown on the page.

Manually Hide Content
---------------------

To manually hide a piece of content, locate it in the adaptive release table and select the "Force hidden" checkbox.
Then click "Save Schedule". Access to the content will be restricted and the content will not be shown to students in
introduction or part pages.

Follow the same procedure, but unticking the box, to make the content available again.

Adaptive Release Schedule
-------------------------

To show a piece of content only after a certain time, only until a certain time, or both, locate the content
in the table and populate the "Start Date & Time" and/or "End Date & Time" entries using the date picker.

After selecting the dates and times for all of the rows you want to release by schedule, click the "Save Schedule" button to
commit the changes.

 * Content with a "Start Date & Time" set will be hidden unless the current date is after the start date.

 * Content with an "End Date & Time" set will be hidden unless the current date is before the end date.

 * Content with both dates set will only be available between the two dates.

.. warning::
   If you are using a course GUID to populate multiple Chirun LTI items with the same content, you must set the adaptive
   release setting on every indiviual LTI item in the VLE.

   The adpative release settings only apply to the current LTI item, even if there are mutliple LTI items sharing uploaded content.
