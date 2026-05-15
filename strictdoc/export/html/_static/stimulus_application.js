(function () {
  /*
  Keep Stimulus application startup in this external script instead of an
  inline <script> next to stimulus_umd.min.js. Turbo compares head scripts by
  their literal src attributes during page visits. StrictDoc pages at different
  document depths can reference the same asset as both "_static/..." and
  "../_static/..."; Turbo then treats stimulus_umd.min.js as a new script and
  executes it again, recreating window.Stimulus and dropping our custom
  Stimulus.application property. Because inline scripts are not replayed in
  that head-merge case, controller scripts can then fail at
  Stimulus.application.register(...). Keeping this startup code external makes
  Turbo execute it after any reloaded Stimulus UMD script, restoring the shared
  application before local controllers register themselves.

  One concrete case is deleting a document from its document screen. The
  confirmation action uses Turbo to send the DELETE request and then follows the
  server redirect back to the project index without a full browser reload. That
  visit crosses from a nested document URL, where assets are referenced with
  "../_static/...", to the root project index, where assets are referenced with
  "_static/...". This is precisely when Turbo may re-run the Stimulus UMD bundle
  during the head merge, so this external startup script must run as part of the
  same visit.
  */
  if (!window.Stimulus || !window.Stimulus.Application) {
    console.error(
      "StrictDoc: Stimulus application could not start because Stimulus is not loaded."
    );
    return;
  }

  if (!window.Stimulus.application) {
    window.Stimulus.application = window.Stimulus.Application.start();
  }
})();
