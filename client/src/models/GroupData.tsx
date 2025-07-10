export interface GroupData {
  id: number;
  name: string;
  university: string;
  description: string;
  imageUrl: string;
  filesServiceUrl?: string | null;
  ownerUsername?: string;
  memberUsernames: string[]; //  List of usernames who are members
  isMember: boolean; //  Indicates if the current user is a member
}
