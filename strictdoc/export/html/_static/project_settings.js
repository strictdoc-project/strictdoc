(() => {
  const getModalTarget = () => document.getElementById('modal');

  const removeProjectSettingsModal = () => {
    const modalTarget = getModalTarget();
    if (modalTarget) modalTarget.replaceChildren();
  };

  // A failed request (network error, or a non-2xx response such as a 500
  // error page) must not be poured into the modal as raw HTML: the server's
  // error page is a full document, not a modal fragment, and would corrupt
  // the current page. Show a minimal, safe, dismissible notice instead,
  // built from static markup that mirrors components/modal/index.jinja so
  // the existing global Close/Escape handling in modal.js applies for free.
  const showProjectSettingsRequestError = () => {
    getModalTarget().innerHTML = `
      <turbo-frame data-js-modal>
        <sdoc-backdrop>
          <sdoc-modal context="project_settings">
            <sdoc-modal-header data-testid="modal-header">Project settings</sdoc-modal-header>
            <sdoc-modal-container>
              <sdoc-form-error data-testid="project-settings-request-error">
                Something went wrong while contacting the server. Please try again.
              </sdoc-form-error>
            </sdoc-modal-container>
            <button data-js-modal-cancel-button type="button" class="action_button" data-action-type="cancel" data-testid="form-cancel-action">Close</button>
          </sdoc-modal>
        </sdoc-backdrop>
      </turbo-frame>
    `;
  };

  const serializeFormEntries = (container) => JSON.stringify(
    Array.from(new FormData(container.closest('form')).entries())
      .filter(([entryName]) => container.querySelector(`[name="${entryName}"]`))
      .sort(([leftName, leftValue], [rightName, rightValue]) => {
        const nameComparison = leftName.localeCompare(rightName);
        return nameComparison || String(leftValue).localeCompare(String(rightValue));
      }),
  );

  const initializeProjectSettingsForm = (projectSettingsForm) => {
    const projectSettingsModal = projectSettingsForm.closest('[data-js-modal]');
    const initialFormEntries = JSON.stringify(
      Array.from(new FormData(projectSettingsForm).entries()).sort(
        ([leftName, leftValue], [rightName, rightValue]) => {
          const nameComparison = leftName.localeCompare(rightName);
          return nameComparison || String(leftValue).localeCompare(String(rightValue));
        },
      ),
    );
    const initialFieldEntries = new Map();
    projectSettingsForm.querySelectorAll('[data-js-project-settings-field]')
      .forEach((settingsField) => {
        initialFieldEntries.set(settingsField, serializeFormEntries(settingsField));
      });

    const serializeProjectSettingsForm = () => JSON.stringify(
      Array.from(new FormData(projectSettingsForm).entries()).sort(
        ([leftName, leftValue], [rightName, rightValue]) => {
          const nameComparison = leftName.localeCompare(rightName);
          return nameComparison || String(leftValue).localeCompare(String(rightValue));
        },
      ),
    );

    const projectSettingsFormHasChanges = () => (
      serializeProjectSettingsForm() !== initialFormEntries
    );

    const updateAllFeaturesOverride = () => {
      const allFeaturesControl = projectSettingsForm.querySelector(
        '[data-js-project-settings-all-features]',
      );
      const individualFeaturesContainer = projectSettingsForm.querySelector(
        '[data-js-project-settings-individual-features]',
      );
      if (!allFeaturesControl || !individualFeaturesContainer) return;

      // ALL_FEATURES changes effective behavior without changing the user's
      // stored individual selections. The controls stay successful form values
      // while pointer and keyboard interaction is suspended.
      individualFeaturesContainer.toggleAttribute(
        'data-disabled',
        allFeaturesControl.checked,
      );
      individualFeaturesContainer.querySelectorAll('input').forEach(
        (featureControl) => {
          featureControl.tabIndex = allFeaturesControl.checked ? -1 : 0;
          featureControl.setAttribute(
            'aria-disabled',
            String(allFeaturesControl.checked),
          );
        },
      );
    };

    const updateProjectSettingsFormState = () => {
      const formHasChanges = projectSettingsFormHasChanges();
      updateAllFeaturesOverride();
      const dismissButton = projectSettingsModal.querySelector(
        '[data-js-project-settings-dismiss]',
      );
      dismissButton.title = formHasChanges ? 'Discard changes' : 'Close settings';
      dismissButton.querySelector(
        '[data-js-project-settings-dismiss-label]',
      ).textContent = formHasChanges ? 'Cancel' : 'Close';

      const applyButton = projectSettingsModal.querySelector(
        '[data-js-project-settings-apply]',
      );
      if (applyButton) applyButton.disabled = !formHasChanges;

      projectSettingsForm.querySelectorAll('[data-js-project-settings-field]')
        .forEach((settingsField) => {
          const fieldHasChanges = (
            serializeFormEntries(settingsField) !== initialFieldEntries.get(settingsField)
          );
          settingsField.toggleAttribute('data-changed', fieldHasChanges);
          settingsField.querySelector(
            '[data-js-project-settings-changed-marker]',
          ).hidden = !fieldHasChanges;
        });
    };

    const requestProjectSettingsClose = () => {
      const discardConfirmation = projectSettingsModal.querySelector(
        '[data-js-project-settings-discard-confirmation]',
      );
      // Once the confirmation is visible, a repeated close request confirms
      // the action. This makes two consecutive Escape presses behave like
      // opening the confirmation and choosing Discard.
      if (!discardConfirmation.hidden) {
        removeProjectSettingsModal();
        return;
      }
      if (!projectSettingsFormHasChanges()) {
        removeProjectSettingsModal();
        return;
      }
      discardConfirmation.hidden = false;
    };

    projectSettingsForm.addEventListener('input', () => {
      updateProjectSettingsFormState();
    });
    projectSettingsForm.addEventListener('change', () => {
      updateProjectSettingsFormState();
    });
    projectSettingsForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      let response;
      try {
        response = await fetch(projectSettingsForm.action, {
          method: 'POST',
          body: new FormData(projectSettingsForm),
        });
      } catch (error) {
        showProjectSettingsRequestError();
        return;
      }
      if (response.status === 204) {
        removeProjectSettingsModal();
        return;
      }
      if (!response.ok) {
        showProjectSettingsRequestError();
        return;
      }
      getModalTarget().innerHTML = await response.text();
      const replacementForm = getModalTarget().querySelector(
        '[data-js-project-settings-form]',
      );
      if (replacementForm) initializeProjectSettingsForm(replacementForm);
    });

    projectSettingsModal.querySelector(
      '[data-js-project-settings-dismiss]',
    ).addEventListener('click', removeProjectSettingsModal);
    projectSettingsModal.querySelector(
      '[data-js-project-settings-confirm-discard]',
    ).addEventListener('click', removeProjectSettingsModal);
    projectSettingsModal.querySelector(
      '[data-js-project-settings-continue-editing]',
    ).addEventListener('click', () => {
      projectSettingsModal.querySelector(
        '[data-js-project-settings-discard-confirmation]',
      ).hidden = true;
    });
    projectSettingsModal.addEventListener(
      'settings:close-requested',
      requestProjectSettingsClose,
    );
    updateProjectSettingsFormState();
  };

  document.addEventListener('click', async (event) => {
    const projectSettingsButton = event.target.closest?.(
      '[data-js-project-settings]',
    );
    if (!projectSettingsButton) return;
    event.preventDefault();
    let response;
    try {
      response = await fetch(projectSettingsButton.href);
    } catch (error) {
      showProjectSettingsRequestError();
      return;
    }
    if (!response.ok) {
      showProjectSettingsRequestError();
      return;
    }
    getModalTarget().innerHTML = await response.text();
    initializeProjectSettingsForm(
      getModalTarget().querySelector('[data-js-project-settings-form]'),
    );
  });
})();
