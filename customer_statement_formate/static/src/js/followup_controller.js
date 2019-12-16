odoo.define('customer_statement_formate.FollowupController', function (require) {
"use strict";

    var core = require('web.core');
    var FollowupFormController = require('accountReports.FollowupFormController');
    // var FollowupFormController2 = require('accountReportsFollowup.FollowupFormController');
    var crash_manager = require('web.crash_manager');
    var framework = require('web.framework');
    var session = require('web.session');


    var QWeb = core.qweb;

    FollowupFormController.include({
        renderButtons: function ($node) {
            this.$buttons = $(QWeb.render("CustomerStatements.buttons", {
                widget: this
            }));
            this.$buttons.on('click',
                '.o_account_reports_followup_print_letter_button',
                this._onPrintLetter.bind(this));
            this.$buttons.on('click',
                '.o_account_reports_followup_print_pdf_button',
                this._onPrintPdf.bind(this));
            this.$buttons.on('click',
                '.o_account_reports_followup_print_xlsx_button',
                this._onPrintxlsx.bind(this));
            this.$buttons.on('click',
                '.o_account_reports_followup_send_mail_button',
                this._onSendMail.bind(this));
            this.$buttons.on('click',
                '.o_account_reports_followup_do_it_later_button',
                this._onDoItLater.bind(this));
            this.$buttons.on('click',
                '.o_account_reports_followup_done_button',
                this._onDone.bind(this));
            this.$buttons.appendTo($node);
        },
        _onPrintPdf: function () {
            var self = this;
            var partnerID = this.model.get(this.handle, {raw: true}).res_id;
            var records = {
                ids: [partnerID],
            };
            this._rpc({
                model: 'account.followup.report',
                method: 'print_pdf_followups',
                args: [records],
            })
            .then(function (result) {
                self.do_action(result);
            });
        },
        _onPrintxlsx: function () {
            var self = this;
            var partnerID = this.model.get(this.handle, {raw: true}).res_id;
            framework.blockUI();
            var def = $.Deferred();
            session.get_file({
                url: '/account_reports/followup_report/xlsx/' + partnerID + '/',
                success: def.resolve.bind(def),
                error: function () {
                    crash_manager.rpc_error.apply(crash_manager, arguments);
                    def.reject();
                },
                complete: framework.unblockUI,
            });
            return def;
        }
    });

    // FollowupFormController2.include({
    //     renderButtons: function ($node) {
    //         this.$buttons = $(QWeb.render("CustomerStatements.buttonsWithLevels", {
    //             widget: this,
    //             action_name: this.model.get(this.handle).data.followup_level.manual_action_note
    //         }));
    //         this.$buttons.on('click', '.o_account_reports_followup_print_letter_button',
    //             this._onPrintLetter.bind(this));
    //         this.$buttons.on('click', '.o_account_reports_followup_print_pdf_button',
    //             this._onPrintPdf.bind(this));
    //         this.$buttons.on('click', '.o_account_reports_followup_print_xlsx_button',
    //             this._onPrintxlsx.bind(this));
    //         this.$buttons.on('click', '.o_account_reports_followup_send_mail_button',
    //             this._onSendMail.bind(this));
    //         this.$buttons.on('click', '.o_account_reports_followup_manual_action_button',
    //             this._onManualAction.bind(this));
    //         this.$buttons.on('click', '.o_account_reports_followup_do_it_later_button',
    //             this._onDoItLater.bind(this));
    //         this.$buttons.on('click', '.o_account_reports_followup_done_button',
    //             this._onDone.bind(this));
    //         this.$buttons.appendTo($node);
    //     }
    // });

});