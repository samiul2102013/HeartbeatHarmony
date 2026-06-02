import { requestJson } from "../core/client";

const extractData = (res: any) => res?.data ?? res;

export const getAdminProfile = () =>
  requestJson("/api/users/profile/").then(extractData);

export const updateAdminProfile = (data: {
  username?: string;
  institute_name?: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone_number?: string;
  avatar?: File | null;
}) => {
  const body = new FormData();
  if (data.username !== undefined) body.append("username", data.username);
  if (data.institute_name !== undefined) body.append("institute_name", data.institute_name);
  if (data.first_name !== undefined) body.append("first_name", data.first_name);
  if (data.last_name !== undefined) body.append("last_name", data.last_name);
  if (data.email !== undefined) body.append("email", data.email);
  if (data.phone_number !== undefined) body.append("phone_number", data.phone_number);
  if (data.avatar) body.append("avatar", data.avatar);

  return requestJson("/api/users/profile/", {
    method: "PATCH",
    body,
    skipContentType: true,
  }).then(extractData);
};

export const changeAdminPassword = (data: {
  old_password: string;
  new_password: string;
}) =>
  requestJson("/api/users/change-password/", {
    method: "POST",
    body: JSON.stringify(data),
  }).then(extractData);
  