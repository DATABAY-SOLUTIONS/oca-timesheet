# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestHrTimesheetSheetAutodraft(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResUsers = cls.env["res.users"]
        cls.Company = cls.env["res.company"]
        cls.Project = cls.env["project.project"]
        cls.HrEmployee = cls.env["hr.employee"]
        cls.HrTimesheetSheet = cls.env["hr_timesheet.sheet"]
        cls.AccountAnalyticLine = cls.env["account.analytic.line"]
        cls.company_id = cls.env.company

    def test_no_autocreate_by_default(self):
        user = self.ResUsers.sudo().create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": self.company_id.id,
            }
        )
        employee = self.HrEmployee.create({"name": "Employee", "user_id": user.id})
        project = self.Project.create({"name": "Project"})

        aal = self.AccountAnalyticLine.create(
            {"project_id": project.id, "employee_id": employee.id, "name": "Time Entry"}
        )

        self.assertFalse(aal.sheet_id)

    def test_autocreate(self):
        user = self.ResUsers.sudo().create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": self.company_id.id,
            }
        )
        employee = self.HrEmployee.create({"name": "Employee", "user_id": user.id})
        project = self.Project.create({"name": "Project"})

        aal_1 = self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "name": "Time Entry 1",
            }
        )

        self.company_id.timesheet_sheets_autodraft = True

        aal_2 = self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "name": "Time Entry 2",
            }
        )

        self.assertTrue(aal_1.sheet_id)
        self.assertTrue(aal_2.sheet_id)
        self.assertEqual(aal_1.sheet_id, aal_2.sheet_id)

    def test_already_confirmed(self):
        user = self.ResUsers.sudo().create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": self.company_id.id,
            }
        )
        employee = self.HrEmployee.create({"name": "Employee", "user_id": user.id})
        project = self.Project.create({"name": "Project"})

        self.company_id.timesheet_sheets_autodraft = True

        aal_1 = self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "name": "Time Entry 1",
            }
        )

        aal_1.sheet_id.with_user(user).action_timesheet_confirm()

        aal_2 = self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "name": "Time Entry 2",
            }
        )
        self.assertFalse(aal_2.sheet_id)

    def test_repeated_auto_draft(self):
        user = self.ResUsers.sudo().create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": self.company_id.id,
            }
        )
        employee = self.HrEmployee.create({"name": "Employee", "user_id": user.id})
        project = self.Project.create({"name": "Project"})

        self.company_id.timesheet_sheets_autodraft = True

        aal = self.AccountAnalyticLine.create(
            {"project_id": project.id, "employee_id": employee.id, "name": "Time Entry"}
        )
        sheet = aal.sheet_id

        aal.sheet_id.with_user(user).action_timesheet_confirm()

        aal.action_autodraft_timesheet_sheets()

        self.assertEqual(aal.sheet_id, sheet)

    def test_manual_autodraft_timesheet_sheet(self):
        user = self.ResUsers.sudo().create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": self.company_id.id,
            }
        )
        employee = self.HrEmployee.create({"name": "Employee", "user_id": user.id})
        project = self.Project.create({"name": "Project"})

        self.company_id.timesheet_sheets_autodraft = True

        aal = self.AccountAnalyticLine.with_context(
            manual_autodraft_timesheet_sheet=True
        ).create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "name": "Time Entry",
            }
        )
        self.assertTrue(aal.sheet_id)
